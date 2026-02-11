# Product Requirements Document (PRD) - Restaurant POS System

## 1. Project Overview
Project ini adalah sistem Backend terpadu (Unified Backend) untuk manajemen restoran yang mendukung tiga platform sekaligus: **Mobile (Customer)**, **Web (Admin)**, dan **Desktop (Cashier)**.

## 2. Objectives
- Mengelola siklus pesanan dari meja dipesan hingga pembayaran selesai.
- Menjamin akurasi stok (Inventory) dengan perlindungan terhadap Race Conditions.
- Menyediakan autentikasi berbasis peran (RBAC) untuk Admin, Staff (Waiters/Cashier), dan Customer.

## 3. User Roles & Permissions
| Role | Permissions |
| :--- | :--- |
| **Admin** | Full access: CRUD Menu, Category, User, Table, dan melihat rincian transaksi. |
| **Staff (Waiters/Cashier)** | Create Order, Update Order Status, Manage Table, Update Stock. |
| **Customer** | Registrasi, melihat Menu, dan melakukan pemesanan (Order). |

## 4. Key Features & Flow
### A. Order Lifecycle
1. **Pemesanan**: Pesanan dibuat -> Stok menu berkurang otomatis -> Status meja berubah menjadi `booked`.
2. **Pelayanan**: Status order berubah menjadi `preparing` lalu `served`.
3. **Pembayaran**: Status payment berubah menjadi `paid` -> **Sistem otomatis mengubah status meja menjadi `available`**.

### B. Inventory Management
- **Atomic Updates**: Penambahan stok (Restock) menggunakan operasi atomik SQL untuk mencegah kehilangan data saat banyak admin input bersamaan.
- **Pessimistic Locking**: Saat pemesanan, sistem mengunci baris database menu terkait untuk memastikan pelanggan tidak memesan item yang stoknya sedang dihitung oleh transaksi lain.
- **Soft Delete**: Menu tidak dihapus permanen, melainkan statusnya diubah menjadi `outOfStock`.

## 5. Technical Stack
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (Supabase) dengan Connection Pooling.
- **ORM**: SQLAlchemy.
- **Security**: JWT Authentication & Bcrypt Hashing.
- **Validation**: Pydantic v2.

## 6. Database Schema (Simplified)
- `Users` & `UserDetails/StaffDetails`: Menyimpan data kredensial dan profil.
- `Tables`: Kelola status ketersediaan meja fisik.
- `Category` & `Menu`: Hierarki makanan/minuman dan sisa porsi harian.
- `Orders` & `DetailedOrder`: Header transaksi dan rincian item yang dipesan.
- `Update_Stock`: Log riwayat penambahan stok oleh staff.
