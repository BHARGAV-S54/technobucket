# Techno Bucket

A modern, production-ready portfolio services website built with TanStack Start, Convex, and Tailwind CSS.

## Features

- **Multi-page Application** with tab-based navigation
- **Portfolio Order Form** with file uploads
- **Admin Dashboard** for order management
- **Responsive Design** for all devices
- **Real-time Backend** with Convex

## Services Offered

1. **ATS-Friendly Resume** - ₹99
2. **Portfolio Website** - ₹1999
3. **Custom Project** - ₹4999
4. **Professional Profile Creation** - ₹999
5. **Complete Career Combo Pack** - ₹1,300 (Save ₹368)

## Tech Stack

- **Frontend**: TanStack Start (React), Tailwind CSS v4
- **Backend**: Convex (real-time database)
- **Auth**: Convex Auth (Password-based)
- **Icons**: Lucide React

## Project Structure

```
├── convex/                 # Backend functions
│   ├── schema.ts          # Database schema
│   ├── auth.ts            # Authentication config
│   ├── portfolioOrders.ts # Order management API
│   └── users.ts           # User management
├── src/
│   ├── components/        # Shared components
│   │   ├── Navbar.tsx     # Navigation component
│   │   └── LightRays.tsx  # Background component
│   ├── routes/            # Page routes
│   │   ├── index.tsx      # Home page
│   │   ├── services.tsx   # Services page
│   │   ├── contact.tsx    # Contact page
│   │   ├── portfolio-order.tsx # Order form
│   │   └── admin.tsx      # Admin dashboard
│   ├── router.tsx         # Router configuration
│   └── styles/            # Global styles
├── public/                # Static assets
└── package.json
```

## Routes

| Route | Description |
|-------|-------------|
| `/` | Home page with features and testimonials |
| `/services` | All services with pricing |
| `/contact` | Contact form |
| `/portfolio-order` | Portfolio order form |
| `/admin` | Admin dashboard |

## Admin Access

- **URL**: `/admin`
- **Username**: `technobucket`
- **Password**: `bhargav`

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Environment Variables

Create `.env.local`:

```env
VITE_CONVEX_URL=your_convex_url
```

## Database Schema

### Users Table
- Authentication and admin roles

### Portfolio Orders Table
- Customer orders for portfolio websites
- Stores: personal info, links, skills, file references, status

## Deployment

1. Push to Convex: `npx convex deploy`
2. Build frontend: `npm run build`
3. Deploy to your hosting platform

## License

© 2025 Techno Bucket. All rights reserved.
