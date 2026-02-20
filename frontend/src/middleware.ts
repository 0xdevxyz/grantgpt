import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const authStorage = request.cookies.get('auth-storage');
  const isAuthenticated = authStorage?.value ? true : false;

  // Protected routes
  const protectedPaths = ['/dashboard', '/grants', '/applications'];
  const isProtectedRoute = protectedPaths.some((path) =>
    request.nextUrl.pathname.startsWith(path)
  );

  // Redirect to login if not authenticated and trying to access protected route
  if (isProtectedRoute && !isAuthenticated) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', request.nextUrl.pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Redirect to dashboard if authenticated and trying to access login/register
  if (
    isAuthenticated &&
    (request.nextUrl.pathname === '/login' ||
      request.nextUrl.pathname === '/register')
  ) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/grants/:path*', '/applications/:path*', '/login', '/register'],
};
