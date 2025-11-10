"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface Application {
  id: string;
  project_title: string;
  status: string;
  completion_percentage: number;
  created_at: string;
  requested_funding: number;
}

export default function DashboardPage() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchApplications = async () => {
      try {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8008";
        
        // For now, without auth, we'll show an empty state
        // Later this will fetch user's applications: /api/v1/applications/
        
        setApplications([]);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching applications:", error);
        setApplications([]);
        setLoading(false);
      }
    };

    fetchApplications();
  }, []);

  const getStatusBadge = (status: string) => {
    const badges: Record<string, { label: string; className: string }> = {
      draft: { label: "Entwurf", className: "bg-gray-200 text-gray-800" },
      generating: { label: "Generierung...", className: "bg-blue-200 text-blue-800" },
      in_progress: { label: "In Bearbeitung", className: "bg-yellow-200 text-yellow-800" },
      review: { label: "Zur Prüfung", className: "bg-purple-200 text-purple-800" },
      ready: { label: "Bereit", className: "bg-green-200 text-green-800" },
      submitted: { label: "Eingereicht", className: "bg-indigo-200 text-indigo-800" },
      approved: { label: "Bewilligt", className: "bg-emerald-200 text-emerald-800" },
      rejected: { label: "Abgelehnt", className: "bg-red-200 text-red-800" },
    };

    const badge = badges[status] || badges.draft;
    return (
      <span className={`px-3 py-1 rounded-full text-xs font-medium ${badge.className}`}>
        {badge.label}
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">GrantGPT Dashboard</h1>
            <Link
              href="/dashboard/new"
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition"
            >
              + Neuer Antrag
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h3 className="text-sm font-medium text-gray-500">Anträge gesamt</h3>
            <p className="text-3xl font-bold text-gray-900 mt-2">{applications.length}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h3 className="text-sm font-medium text-gray-500">In Bearbeitung</h3>
            <p className="text-3xl font-bold text-blue-600 mt-2">
              {applications.filter((a) => a.status === "in_progress").length}
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h3 className="text-sm font-medium text-gray-500">Eingereicht</h3>
            <p className="text-3xl font-bold text-indigo-600 mt-2">
              {applications.filter((a) => a.status === "submitted").length}
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <h3 className="text-sm font-medium text-gray-500">Bewilligt</h3>
            <p className="text-3xl font-bold text-green-600 mt-2">
              {applications.filter((a) => a.status === "approved").length}
            </p>
          </div>
        </div>

        {/* Applications List */}
        <div className="bg-white rounded-lg shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Meine Anträge</h2>
          </div>

          {loading ? (
            <div className="px-6 py-12 text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-2 text-gray-500">Lade Anträge...</p>
            </div>
          ) : applications.length === 0 ? (
            <div className="px-6 py-12 text-center">
              <div className="max-w-md mx-auto">
                <div className="text-6xl mb-4">💎</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Willkommen bei GrantGPT!
                </h3>
                <p className="text-gray-500 mb-6">
                  Noch keine Anträge vorhanden. Finden Sie jetzt passende Förderprogramme für Ihr Projekt!
                </p>
                <div className="flex flex-col sm:flex-row gap-3 justify-center">
                  <Link
                    href="/grants/search"
                    className="inline-block bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition"
                  >
                    🔍 Förderprogramme finden
                  </Link>
                  <Link
                    href="/dashboard/new"
                    className="inline-block border border-gray-300 hover:border-gray-400 text-gray-700 px-6 py-3 rounded-lg font-medium transition"
                  >
                    + Neuer Antrag
                  </Link>
                </div>
                <div className="mt-8 grid grid-cols-3 gap-6 text-center">
                  <div>
                    <div className="text-2xl font-bold text-blue-600">57+</div>
                    <div className="text-xs text-gray-600">Programme</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-blue-600">160 Mrd.€</div>
                    <div className="text-xs text-gray-600">Fördermittel</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-blue-600">2h</div>
                    <div className="text-xs text-gray-600">statt 80h</div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {applications.map((app) => (
                <Link
                  key={app.id}
                  href={`/dashboard/application/${app.id}`}
                  className="block px-6 py-4 hover:bg-gray-50 transition"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-medium text-gray-900">{app.project_title}</h3>
                      <div className="mt-1 flex items-center space-x-4 text-sm text-gray-500">
                        <span>Erstellt: {new Date(app.created_at).toLocaleDateString("de-DE")}</span>
                        <span>•</span>
                        <span>Fördersumme: {app.requested_funding.toLocaleString("de-DE")} €</span>
                      </div>
                      {/* Progress Bar */}
                      {app.status === "in_progress" && (
                        <div className="mt-3">
                          <div className="flex justify-between text-xs text-gray-500 mb-1">
                            <span>Fortschritt</span>
                            <span>{app.completion_percentage}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full transition-all"
                              style={{ width: `${app.completion_percentage}%` }}
                            ></div>
                          </div>
                        </div>
                      )}
                    </div>
                    <div className="ml-6">{getStatusBadge(app.status)}</div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

