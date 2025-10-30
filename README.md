# TodoList – Full-Featured Task Manager with Categories & Filters

A **secure, production-ready todo-list application**, built using:

- **Backend**: Python + Django + Django REST Framework  
- **Database**: **PostgreSQL** (Production) / SQLite (local)  
- **Frontend**: **Flutter** (Android & iOS)  
- **Authentication**: JWT + Email OTP  

---

## Features
| Feature | Status |
|--------|--------|
| Register with **Email OTP verification** | Done |
| Login (email/password) | Done |
| **Forgot / Reset Password** (OTP) | Done |
| **Profile Management** (edit, picture) | Done |
| **Create / List / Update / Delete Todos** | Done |
| **Category CRUD** (group tasks) | Done |
| **Filter & Search Todos** (`status`, `category`, `search`) | Done |
| **User Management System** (Admin Panel) | Done |
| **Pending Registration Approval** (Admin only) | Done |
| **Super Admin** (Full control) | Done |
| **Flutter Mobile App** | Done |
| **PostgreSQL + Whitenoise + Railway/Render Deploy** | Done |

---

## User Management System

| Role | Permissions |
|------|-------------|
| **Regular User** | View own todos, profile, categories |
| **Admin** | Approve/reject pending users, view all users, manage todos |
| **Super Admin** | Full access: delete users, manage admins, system settings |

> **Pending Users** → Must be approved by **Admin** via `/api/pending-registrations/`  
> Only **approved users** can log in.

---

## Mobile App Screenshots (Flutter)

**All screenshots shown in original size – 3 per row.**

| | | |
|---|---|---|
| **Login** | **Register** | **All Todos** |
| ![login](https://github.com/Kawsar07/todolistapi/blob/main/screenshorts/login.png?raw=true) | ![register](https://github.com/Kawsar07/todolistapi/blob/main/screenshorts/register.png?raw=true) | ![alltodo](https://github.com/Kawsar07/todolistapi/blob/main/screenshorts/alltodo.png?raw=true) |
| **Profile Drawer** | **Filter Todo** | **Change Password** |
| ![profiledrawer](https://github.com/Kawsar07/todolistapi/blob/main/screenshorts/profiledrawer.png?raw=true) | ![filtertodo](https://github.com/Kawsar07/todolistapi/blob/main/screenshorts/filtertodo.png?raw=true) | ![changepassword](https://github.com/Kawsar07/todolistapi/blob/main/screenshorts/chnagepassword.png?raw=true) |
| **Forget Password** | **Verify OTP** | **Reset Password** |
| ![forget](https://github.com/Kawsar07/todolistapi/blob/main/screenshorts/forget.png?raw=true) | ![verify_otp](https://github.com/Kawsar07/todolistapi/blob/main/screenshorts/verify_otp.png?raw=true) | ![reset_password](https://github.com/Kawsar07/todolistapi/blob/main/screenshorts/reset_password.png?raw=true) |
| **Task Details** | **All Users (Admin)** | **Task Edit** |
| ![task_details](https://github.com/Kawsar07/todolistapi/blob/main/screenshorts/task_details.png?raw=true) | ![usermanagmentallusers](https://github.com/Kawsar07/todolistapi/blob/main/screenshorts/usermanagmentallusers.png?raw=true) | ![task_edit](https://github.com/Kawsar07/todolistapi/blob/main/screenshorts/task_edit.png?raw=true) |
| **Edit Profile** | **Add Task** | **Pending Registrations (Admin)** |
| ![editprofile](https://github.com/Kawsar07/todolistapi/blob/main/screenshorts/editprofile.png?raw=true) | ![newtaskadd](https://github.com/Kawsar07/todolistapi/blob/main/screenshorts/newtaskadd.png?raw=true) | ![pending](https://github.com/Kawsar07/todolistapi/blob/main/screenshorts/pending.png?raw=true) |
| **Add Category** | | |
| ![catgoryadd](https://github.com/Kawsar07/todolistapi/blob/main/screenshorts/catgoryadd.png?raw=true) | | |

> **All 14 screenshots** are in `screenshorts/` – displayed **as uploaded**.

---

## API Endpoints (Full Documentation)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/api/register/` | Register + send OTP | No |
| `POST` | `/api/login/` | Login → JWT tokens | No |
| `POST` | `/api/forgot-password/` | Send reset OTP | No |
| `POST` | `/api/verify-otp/` | Verify OTP (register or reset) | No |
| `POST` | `/api/change-password/` | Set new password after OTP | No |
| `GET/PUT` | `/api/profile/` | Get / Update own profile | Yes |
| `GET` | `/api/todo/` | List todos (filter, search, ordering) | Yes |
| `POST` | `/api/todo/` | Create new todo | Yes |
| `GET/PUT/DELETE` | `/api/todo/<pk>/` | Todo detail | Yes |
| `GET` | `/api/categories/` | List categories | Yes |
| `POST` | `/api/categories/` | Create category | Yes |
| `GET/PUT/DELETE` | `/api/categories/<pk>/` | Category detail | Yes |
| `GET` | `/api/users/` | List all users **(Admin only)** | Yes |
| `GET` | `/api/users/search/?search=john` | Search users **(Admin)** | Yes |
| `GET` | `/api/users/<user_id>/` | User detail **(Admin)** | Yes |
| `GET` | `/api/pending-registrations/` | List pending users **(Admin only)** | Yes |
| `GET/PUT/DELETE` | `/api/pending-registrations/<pk>/` | Approve/Reject user **(Admin only)** | Yes |

> **Filter examples**  
> - `/api/todo/?status=pending&category=1&search=meeting`  
> - `/api/todo/?ordering=-due_date`

---

## Project Structure

```text
todolistapi/
├── EmployeeApp/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views/
│   │   ├── register.py
│   │   ├── login.py
│   │   ├── profile.py
│   │   ├── todo.py
│   │   ├── category.py
│   │   ├── forgot_password.py
│   │   ├── otp_verification.py
│   │   ├── change_password.py
│   │   ├── user_management.py
│   │   └── pending_registration.py
│   ├── serializers.py
│   ├── urls.py
│   └── tests.py
├── myproject/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── media/
│   └── profiles/
├── screenshorts/         
├── staticfiles/
├── manage.py
├── requirements.txt
├── .env.example
├── README.md
└── .gitignore
