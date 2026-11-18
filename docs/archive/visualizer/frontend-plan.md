> **Histórico, arquivado em 2026-11-17.** Origem: `visualizer/frontend-plan.md`.
> Substituído por: visualizer/IMPLEMENTATION_PLAN.md (também arquivado); hoje, specs/
> Conteúdo original abaixo, sem edição.

# Angular Frontend Implementation Plan — visualizer

> **Documento histórico.** Este foi o plano inicial do front. O plano mantido e
> atualizado (com a numeração 6.1, 6.2, 6.3 etc.) é `IMPLEMENTATION_PLAN.md` na
> mesma pasta. Use este arquivo só como referência de decisões originais.

## 1. Tech Stack & Tooling

| Area | Choice | Rationale |
|------|--------|-----------|
| **Framework** | Angular 18+ (standalone components) | Modern, built-in signals, zoneless optional |
| **Build** | Vite (via `@angular/cli` or Nx) | Fast HMR, smaller bundles |
| **Language** | TypeScript (strict mode) | Type safety with backend DTOs |
| **UI Library** | **Angular Material** + **Tailwind CSS** | Material for data tables/dialogs, Tailwind for layout |
| **State** | **Signals + Services** (no NgRx needed) | Simple, reactive, built-in |
| **Forms** | Reactive Forms | Complex validation, nested forms |
| **HTTP** | `HttpClient` + interceptors | JWT, error handling, loading |
| **Routing** | Angular Router + Guards | Auth, lazy-loaded features |
| **Testing** | Jest + Testing Library | Fast, modern |
| **E2E** | Playwright | Reliable browser tests |

---

## 2. Project Structure

```
visualizer/
├── src/
│   ├── app/
│   │   ├── core/                    # Singleton services, guards, interceptors
│   │   │   ├── auth/
│   │   │   │   ├── auth.service.ts          # login, logout, token storage
│   │   │   │   ├── auth.guard.ts            # canActivate for protected routes
│   │   │   │   ├── auth.interceptor.ts      # JWT header injection
│   │   │   │   └── token.storage.ts         # localStorage wrapper
│   │   │   ├── http/
│   │   │   │   ├── error.interceptor.ts     # global error handling
│   │   │   │   └── loading.interceptor.ts   # global loading spinner
│   │   │   └── core.module.ts
│   │   │
│   │   ├── shared/                  # Reusable UI, pipes, directives
│   │   │   ├── components/
│   │   │   │   ├── loading-spinner/
│   │   │   │   ├── error-display/
│   │   │   │   ├── confirm-dialog/
│   │   │   │   └── page-header/
│   │   │   ├── pipes/
│   │   │   │   ├── currency.pipe.ts
│   │   │   │   ├── percentage.pipe.ts
│   │   │   │   └── profit-loss.pipe.ts
│   │   │   └── validators/
│   │   │       └── password-match.validator.ts
│   │   │
│   │   ├── features/                # Lazy-loaded feature modules
│   │   │   ├── auth/
│   │   │   │   ├── login/
│   │   │   │   │   ├── login.component.ts
│   │   │   │   │   ├── login.component.html
│   │   │   │   │   └── login.component.scss
│   │   │   │   └── auth.routes.ts
│   │   │   │
│   │   │   ├── dashboard/           # Wallet list + summary cards
│   │   │   │   ├── dashboard.component.ts
│   │   │   │   └── dashboard.routes.ts
│   │   │   │
│   │   │   ├── wallets/             # Wallet CRUD
│   │   │   │   ├── wallet-list/
│   │   │   │   ├── wallet-form/     # create/edit dialog
│   │   │   │   ├── wallet-detail/   # assets + transactions tabs
│   │   │   │   └── wallets.routes.ts
│   │   │   │
│   │   │   ├── assets/              # Asset CRUD within wallet
│   │   │   │   ├── asset-list/
│   │   │   │   ├── asset-form/
│   │   │   │   └── assets.routes.ts
│   │   │   │
│   │   │   ├── transactions/        # Transaction CRUD per asset
│   │   │   │   ├── transaction-list/
│   │   │   │   ├── transaction-form/
│   │   │   │   └── transactions.routes.ts
│   │   │   │
│   │   │   └── portfolio/           # Portfolio summary (GET /wallet/{id}/summary)
│   │   │       ├── portfolio.component.ts
│   │   │       └── portfolio.routes.ts
│   │   │
│   │   ├── layout/                  # App shell
│   │   │   ├── header/
│   │   │   ├── sidebar/
│   │   │   └── layout.component.ts
│   │   │
│   │   ├── app.routes.ts            # Root routes + lazy loading
│   │   ├── app.config.ts            # provideHttpClient, provideRouter, etc.
│   │   └── app.component.ts
│   │
│   ├── assets/                      # Static assets
│   ├── environments/
│   │   ├── environment.ts
│   │   └── environment.prod.ts
│   ├── styles.scss                  # Tailwind + Material theme
│   └── main.ts
│
├── angular.json
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── jest.config.ts
├── playwright.config.ts
└── .github/workflows/ci.yml
```

---

## 3. API Endpoints Mapping (Backend → Frontend)

| Feature | Backend Endpoint | Frontend Service Method |
|---------|------------------|-------------------------|
| **Auth** | `POST /auth/login` | `authService.login(email, password)` |
| **Users** | `GET /users` (ADMIN) | `userService.getAll()` |
| **Wallets** | `POST /wallet` | `walletService.create(dto)` |
| | `GET /wallet` | `walletService.getAll()` |
| | `GET /wallet/{id}` | `walletService.getById(id)` |
| | `PUT /wallet/{id}` | `walletService.update(id, dto)` |
| | `DELETE /wallet/{id}` | `walletService.delete(id)` |
| **Assets** | `POST /assets` | `assetService.create(dto)` |
| | `GET /assets?walletId=` | `assetService.getByWallet(walletId)` |
| | `GET /assets/{id}` | `assetService.getById(id)` |
| | `PUT /assets/{id}` | `assetService.update(id, dto)` |
| | `DELETE /assets/{id}` | `assetService.delete(id)` |
| **Transactions** | `POST /transactions` | `txService.create(dto)` |
| | `GET /transactions?assetId=` | `txService.getByAsset(assetId)` |
| | `GET /transactions/{id}` | `txService.getById(id)` |
| | `PUT /transactions/{id}` | `txService.update(id, dto)` |
| | `DELETE /transactions/{id}` | `txService.delete(id)` |
| **Portfolio** | `GET /wallet/{id}/summary` | `portfolioService.getSummary(walletId)` |

---

## 4. Key UI Pages & Flows

```
┌─────────────────────────────────────────────────────────────┐
│  /login                  →  Login Page (email/password)     │
│       │                                                   │
│       ▼ (success)                                         │
│  /dashboard               →  Wallet List + Quick Stats     │
│       │                                                   │
│       ├─► /wallets/new         →  Create Wallet Dialog    │
│       │                                                   │
│       ├─► /wallets/:id         →  Wallet Detail           │
│       │       ├─► Assets Tab   →  Asset List + Add/Edit   │
│       │       │       └─► /assets/new  →  Asset Form      │
│       │       │       └─► /assets/:id  →  Asset Detail    │
│       │       │                           └─► Transactions │
│       │       │                                    Tab     │
│       │       │                                    └─► /tx/new
│       │       │                                    └─► /tx/:id
│       │       └─► Portfolio Tab →  Summary (P&L, alloc)   │
│       │                                                   │
│       └─► /portfolio/:id       →  Full-screen summary     │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Core Implementation Details

### 5.1 Auth Flow
```typescript
// auth.service.ts
login(dto): Observable<LoginResponseDTO> → stores JWT in localStorage
logout(): void → clears storage, navigates to /login
isAuthenticated(): boolean → checks token expiry
getToken(): string | null → for interceptor
```

### 5.2 HTTP Interceptor Chain
```typescript
// auth.interceptor.ts
req = req.clone({ setHeaders: { Authorization: `Bearer ${token}` } });

// error.interceptor.ts
401 → logout + redirect to /login
403 → show "Access denied" toast
500 → show "Server error" toast
```

### 5.3 Portfolio Summary Component (Key Feature)
```typescript
// portfolio.component.ts
summary = signal<PortfolioSummaryDTO | null>(null);
loading = signal(true);
warningAssets = computed(() => summary()?.assets.filter(a => a.warning) ?? []);
```

---

## 6. Phased Implementation

| Phase | Scope | Deliverable |
|-------|-------|-------------|
| **0** | Project init | `ng new`, Tailwind, Material, ESLint/Prettier, CI |
| **1** | Auth + Layout | Login, JWT interceptor, guards, header/sidebar |
| **2** | Dashboard + Wallets | Wallet CRUD, list, create dialog |
| **3** | Assets | Asset CRUD within wallet, inline forms |
| **4** | Transactions | Transaction CRUD per asset, BUY/SELL forms |
| **5** | Portfolio Summary | `/wallet/{id}/summary` view with charts (ngx-charts or Chart.js) |
| **6** | Polish | Validation, toasts, loading states, responsive, a11y |
| **7** | Deploy | Docker multi-stage (nginx + Angular build), docker-compose |

---

## 7. Open Decisions (Need Your Input)

| Decision | Options | Recommendation |
|----------|---------|----------------|
| **State mgmt** | Signals (built-in) vs NgRx | **Signals** — sufficient for this scope |
| **Charts** | ngx-charts, Chart.js, ApexCharts | **ngx-charts** (Angular-native, D3-based) |
| **Date picker** | Material datepicker vs native `<input type="date">` | **Native** — lighter, works mobile |
| **Table** | Material Table vs custom + TanStack Table | **Material Table** — sorting/pagination built-in |
| **Monorepo?** | Separate repo vs Nx workspace with backend | **Separate repos** — simpler CI, independent deploys |
| **Env config** | `environment.ts` vs runtime `window.__env` | **Runtime config** — same Docker image for dev/staging/prod |

---

## 8. Docker Integration (Frontend)

```dockerfile
# Dockerfile.frontend
# Build stage
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build -- --configuration production

# Runtime stage
FROM nginx:alpine
COPY --from=build /app/dist/visualizer/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

```yaml
# docker-compose.yml (add to existing)
  frontend:
    build:
      context: ./visualizer
      dockerfile: Dockerfile
    ports:
      - "4200:80"
    depends_on:
      - app
    environment:
      - API_URL=http://app:8080
```

---

## 9. Next Steps

1. **Confirm decisions** in §7
2. **Create repo** (`visualizer`) with Angular 18 + Vite
3. **Phase 0** — scaffolding, linting, CI
4. **Phase 1** — auth + layout (highest value first)

---

## Questions for you:

1. Monorepo (Nx) or separate frontend repo?
2. Preferred chart library (ngx-charts vs Chart.js)?
3. Runtime env config or build-time `environment.ts`?
4. Any specific UI/UX requirements (dark mode, mobile-first)?