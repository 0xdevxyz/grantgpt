'use client';

import { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/store/auth';

export default function RegisterPage() {
  const router = useRouter();
  const { register, isLoading, error, clearError } = useAuth();
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    company_name: '',
    full_name: '',
  });

  const [validationError, setValidationError] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearError();
    setValidationError('');

    // Validation
    if (formData.password.length < 8) {
      setValidationError('Passwort muss mindestens 8 Zeichen lang sein');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setValidationError('Passwörter stimmen nicht überein');
      return;
    }

    try {
      await register({
        email: formData.email,
        password: formData.password,
        company_name: formData.company_name,
        full_name: formData.full_name || undefined,
      });
      router.push('/dashboard');
    } catch (err) {
      // Error is handled by the store
    }
  };

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const displayError = error || validationError;

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4 py-12">
      <div className="max-w-md w-full bg-white rounded-lg shadow-xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            FörderScout AI
          </h1>
          <p className="text-gray-600">
            Erstellen Sie Ihr kostenloses Konto
          </p>
        </div>

        {displayError && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-600">{displayError}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              E-Mail-Adresse *
            </label>
            <input
              id="email"
              type="email"
              required
              value={formData.email}
              onChange={(e) => handleChange('email', e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="ihre@email.de"
              disabled={isLoading}
            />
          </div>

          <div>
            <label
              htmlFor="company_name"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Firmenname *
            </label>
            <input
              id="company_name"
              type="text"
              required
              value={formData.company_name}
              onChange={(e) => handleChange('company_name', e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Ihre Firma GmbH"
              disabled={isLoading}
            />
          </div>

          <div>
            <label
              htmlFor="full_name"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Ihr Name (optional)
            </label>
            <input
              id="full_name"
              type="text"
              value={formData.full_name}
              onChange={(e) => handleChange('full_name', e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Max Mustermann"
              disabled={isLoading}
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Passwort *
            </label>
            <input
              id="password"
              type="password"
              required
              value={formData.password}
              onChange={(e) => handleChange('password', e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Mindestens 8 Zeichen"
              disabled={isLoading}
            />
          </div>

          <div>
            <label
              htmlFor="confirmPassword"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Passwort bestätigen *
            </label>
            <input
              id="confirmPassword"
              type="password"
              required
              value={formData.confirmPassword}
              onChange={(e) => handleChange('confirmPassword', e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Passwort wiederholen"
              disabled={isLoading}
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors mt-6"
          >
            {isLoading ? 'Wird registriert...' : 'Konto erstellen'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Bereits ein Konto?{' '}
            <Link
              href="/login"
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              Jetzt anmelden
            </Link>
          </p>
        </div>

        <p className="mt-6 text-xs text-gray-500 text-center">
          Mit der Registrierung stimmen Sie unseren{' '}
          <Link href="/terms" className="text-blue-600 hover:underline">
            AGB
          </Link>{' '}
          und{' '}
          <Link href="/privacy" className="text-blue-600 hover:underline">
            Datenschutzbestimmungen
          </Link>{' '}
          zu.
        </p>
      </div>
    </div>
  );
}
