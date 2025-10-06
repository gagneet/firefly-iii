# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Firefly III is a self-hosted personal finance manager built with Laravel (PHP) and featuring dual frontend implementations. It uses a repository pattern architecture with double-entry bookkeeping principles.

**Key Technologies:**
- Backend: Laravel 12, PHP 8.4+, Passport/Sanctum for auth
- Database: MySQL/PostgreSQL/SQLite with Eloquent ORM
- Frontend v1: Vue 2 + Laravel Mix (legacy pages)
- Frontend v2: Alpine.js + Vite (modern pages, AdminLTE 4)
- Testing: PHPUnit with unit/integration/feature test suites
- Code Quality: PHPStan (level 7), Rector, PHP-CS-Fixer

## Architecture

### Namespace Structure

```
FireflyIII\         → app/
Domain\             → domain/ (currently unused, reserved for future DDD refactoring)
Database\Factories\ → database/factories/
Database\Seeders\   → database/seeders/
```

### Key Directories

**Backend:**
- `app/Api/V1/` - REST API controllers, requests, and middleware
- `app/Repositories/` - Data access layer organized by entity (Account, Transaction, Budget, etc.)
- `app/Services/` - Business logic services (FireflyIIIOrg, Internal, Password, Webhook)
- `app/TransactionRules/` - Rule engine for automated transaction processing (Actions, Engine, Expressions, Factory)
- `app/Support/` - Shared utilities, facades, and helper classes
- `app/Http/Controllers/` - Web controllers organized by entity
- `app/Models/` - Eloquent models for database entities
- `app/Transformers/` - API response transformers (using Fractal)
- `app/Console/Commands/` - Artisan commands (Correction, Export, Integrity, System, Tools, Upgrade)

**Frontend:**
- `resources/assets/v1/` - Vue 2 application (legacy, gradually being replaced)
- `resources/assets/v2/` - Alpine.js application (modern, uses Vite)

**Configuration:**
- `.ci/` - Contains PHPStan, Rector, PHP-CS-Fixer, and PHPMD configurations
- `routes/` - Route definitions (api.php, web.php, breadcrumbs.php, channels.php)

### API Architecture

The API follows REST conventions with versioned endpoints (v1):
- Controllers in `app/Api/V1/Controllers/` organized by resource
- API routes use namespace `FireflyIII\Api\V1\Controllers`
- Request validation via dedicated Request classes
- Authentication via Passport OAuth2 or Sanctum tokens

## Development Commands

### PHP/Laravel

**Run tests:**
```bash
# All unit tests (no coverage)
composer unit-test
# Or: vendor/bin/phpunit -c phpunit.xml --testsuite unit --no-coverage

# All integration tests
composer integration-test
# Or: vendor/bin/phpunit -c phpunit.xml --testsuite integration --no-coverage

# Full test suite with coverage
composer coverage
# Or: vendor/bin/phpunit -c phpunit.xml

# Run specific test
vendor/bin/phpunit tests/unit/Path/To/SpecificTest.php
```

**Code quality:**
```bash
# PHPStan static analysis (level 7)
.ci/phpstan.sh
# Or: vendor/bin/phpstan analyse -c .ci/phpstan.neon

# PHP CS Fixer (code style)
.ci/phpcs.sh

# Rector (automated refactoring)
.ci/rector.sh
# Or: vendor/bin/rector process --config .ci/rector.php --dry-run

# PHPMD (mess detector)
.ci/phpmd.sh
```

**Laravel artisan:**
```bash
# Clear caches
php artisan config:clear
php artisan route:clear
php artisan view:clear
php artisan cache:clear
php artisan twig:clean

# Database migrations
php artisan migrate
php artisan migrate:rollback

# Custom Firefly III commands
php artisan firefly-iii:upgrade-database
php artisan firefly-iii:verify-security-alerts
php artisan firefly-iii:laravel-passport-keys
```

### Frontend

**v1 (Vue 2 + Laravel Mix):**
```bash
cd resources/assets/v1
npm install
npm run development    # Build for development
npm run watch         # Watch for changes
npm run production    # Build for production
```

**v2 (Alpine.js + Vite):**
```bash
cd resources/assets/v2
npm install
npm run dev          # Start dev server
npm run build        # Build for production
```

**Root workspace commands:**
```bash
npm install          # Install all workspace dependencies
npm run postinstall  # Apply patches via patch-package
```

## Important Development Notes

### Repository Pattern

Firefly III uses a repository pattern for data access. Never query models directly in controllers or services - always use repositories:

```php
// Good
$accountRepository->findById($id);

// Bad
Account::find($id);
```

Repositories are located in `app/Repositories/` and organized by entity type.

### Transaction Rules Engine

The transaction rules system (`app/TransactionRules/`) allows users to automate transaction processing:
- **Actions/** - Operations applied to transactions (e.g., set category, add tags)
- **Engine/** - Core rule processing logic
- **Expressions/** - Conditions for matching transactions (e.g., description contains, amount equals)
- **Factory/** - Creates rule components from configuration

### Frontend Migration

The project is migrating from Vue 2 (v1) to Alpine.js (v2):
- New features should use v2 (Alpine.js + Vite)
- Legacy pages in v1 will be gradually ported
- Both frontends coexist during transition

### PHPStan Configuration

PHPStan runs at level 7. Specific errors are ignored in `.ci/phpstan.neon`:
- Numeric-string BC math warnings
- Missing generic types
- Dynamic Eloquent method calls
- Custom Eloquent scopes

### Testing

Test suites are defined in `phpunit.xml`:
- **unit** - Fast, isolated tests in `tests/unit/`
- **integration** - Database-dependent tests in `tests/integration/`
- **feature** - End-to-end API/web tests in `tests/feature/`

Tests use SQLite in-memory database (`DB_CONNECTION=sqlite`, `DB_DATABASE=""` in test env).

### Authentication

Multiple auth systems are in place:
- **Passport** - OAuth2 for API (primary)
- **Sanctum** - Token-based API auth (secondary)
- **Session** - Traditional web auth with 2FA support (Google2FA)

### Custom Artisan Commands

Firefly III includes custom commands organized in `app/Console/Commands/`:
- **Correction/** - Fix data inconsistencies
- **Integrity/** - Validate data integrity
- **Upgrade/** - Handle version upgrades
- **System/** - System management tasks
- **Export/** - Data export utilities

## Common Patterns

### Double-Entry Bookkeeping

All transactions involve source and destination accounts with equal amounts. The `app/Support/Steam.php` class contains core financial calculation utilities.

### Multi-User Support

Most models are user-scoped. Always filter by user when querying:
```php
$account->where('user_id', $user->id)->get();
```

### Soft Deletes

Many models use soft deletes. Use `withTrashed()` when needed to include deleted records.

### TransactionGroup Structure

Transactions are grouped via `TransactionGroup` → `TransactionJournal` → `Transaction` hierarchy:
- **TransactionGroup** - Container for related journals (e.g., split transaction)
- **TransactionJournal** - Represents a complete double-entry transaction
- **Transaction** - Individual source or destination entries

### Localization

Translations live in `resources/lang/`. The application supports multiple languages and locales with separate language (display text) and locale (number formatting) settings.

## Environment Setup

Copy `.env.example` to `.env` and configure:
- `APP_KEY` - Generate with `php artisan key:generate`
- Database credentials (MySQL, PostgreSQL, or SQLite)
- `SITE_OWNER` - Admin email for error reporting
- `TZ` - Timezone
- `DEFAULT_LANGUAGE` - Default UI language

## Documentation

- Main docs: https://docs.firefly-iii.org/
- API docs: Auto-generated from routes in `routes/api.php`
- Installation: https://docs.firefly-iii.org/how-to/firefly-iii/installation/
