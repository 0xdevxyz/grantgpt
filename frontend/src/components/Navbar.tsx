'use client';

import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/store/auth';
import { useState } from 'react';

export default function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const { user, isAuthenticated, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const isActive = (path: string) => pathname === path;

  return (
    <nav className="bg-white shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link href={isAuthenticated ? '/dashboard' : '/'} className="flex items-center">
              <div className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                FörderScout AI
              </div>
            </Link>
          </div>

          {/* Desktop Navigation */}
          {isAuthenticated ? (
            <>
              <div className="hidden md:flex items-center space-x-6">
                <Link
                  href="/dashboard"
                  className={`px-3 py-2 text-sm font-medium transition-colors ${
                    isActive('/dashboard')
                      ? 'text-blue-600'
                      : 'text-gray-700 hover:text-blue-600'
                  }`}
                >
                  Dashboard
                </Link>
                <Link
                  href="/grants/search"
                  className={`px-3 py-2 text-sm font-medium transition-colors ${
                    isActive('/grants/search')
                      ? 'text-blue-600'
                      : 'text-gray-700 hover:text-blue-600'
                  }`}
                >
                  Förderprogramme
                </Link>
                <Link
                  href="/dashboard/new"
                  className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
                >
                  + Neuer Antrag
                </Link>
              </div>

              {/* User Menu */}
              <div className="hidden md:flex items-center space-x-4">
                <div className="text-sm text-gray-600">
                  {user?.company_name || user?.email}
                </div>
                <button
                  onClick={handleLogout}
                  className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
                >
                  Abmelden
                </button>
              </div>
            </>
          ) : (
            <div className="hidden md:flex items-center space-x-4">
              <Link
                href="/login"
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors"
              >
                Anmelden
              </Link>
              <Link
                href="/register"
                className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
              >
                Registrieren
              </Link>
            </div>
          )}

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-700 hover:text-blue-600 hover:bg-gray-100 focus:outline-none"
            >
              <span className="sr-only">Menü öffnen</span>
              {mobileMenuOpen ? (
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              )}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-200">
            {isAuthenticated ? (
              <div className="space-y-2">
                <Link
                  href="/dashboard"
                  className="block px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Dashboard
                </Link>
                <Link
                  href="/grants/search"
                  className="block px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Förderprogramme
                </Link>
                <Link
                  href="/dashboard/new"
                  className="block px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  + Neuer Antrag
                </Link>
                <div className="pt-2 border-t border-gray-200 mt-2">
                  <div className="px-4 py-2 text-sm text-gray-600">
                    {user?.company_name || user?.email}
                  </div>
                  <button
                    onClick={() => {
                      handleLogout();
                      setMobileMenuOpen(false);
                    }}
                    className="block w-full text-left px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-md"
                  >
                    Abmelden
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-2">
                <Link
                  href="/login"
                  className="block px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Anmelden
                </Link>
                <Link
                  href="/register"
                  className="block px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Registrieren
                </Link>
              </div>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}
