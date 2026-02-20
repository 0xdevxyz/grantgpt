"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { grantsApi, Grant } from "@/lib/api/grants";

export default function GrantSearchPage() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [budget, setBudget] = useState("");
  const [location, setLocation] = useState("");
  const [results, setResults] = useState<Grant[]>([]);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) {
      setError("Bitte geben Sie eine Projektbeschreibung ein");
      return;
    }

    setSearching(true);
    setError(null);

    try {
      const data = await grantsApi.search({
        project_description: query,
        budget: budget ? parseFloat(budget) : undefined,
        location: location || undefined,
      });
      
      setResults(data);
    } catch (err: any) {
      console.error("Search error:", err);
      setError(err.response?.data?.detail || "Fehler bei der Suche. Bitte versuchen Sie es erneut.");
    } finally {
      setSearching(false);
    }
  };
        deadline: grant.deadline !== "Laufend" ? grant.deadline : null,
        is_continuous: grant.deadline === "Laufend",
      }));

      setResults(mappedResults);
    } catch (error) {
      console.error("Search error:", error);
      alert("Fehler bei der Suche. Bitte versuchen Sie es erneut.");
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900">Fördermittel-Suche</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Form */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Beschreiben Sie Ihr Projekt
          </h2>

          <textarea
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            rows={4}
            placeholder="z.B. Wir wollen eine KI-gestützte Plattform entwickeln, die Fördermittel-Anträge automatisiert. Budget: 300k€. Entwicklungszeit: 18 Monate."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />

          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Budget (optional)
              </label>
              <input
                type="number"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="z.B. 300000"
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Standort (optional)
              </label>
              <input
                type="text"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="z.B. München, Bayern"
              />
            </div>
          </div>

          <button
            onClick={handleSearch}
            disabled={searching || !query.trim()}
            className="mt-6 w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-medium transition"
          >
            {searching ? "Suche läuft..." : "🔍 Passende Förderprogramme finden"}
          </button>
        </div>

        {/* Results */}
        {results.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-gray-900">
              🎯 Top-Matches für Ihr Projekt
            </h2>

            {results.map((grant, index) => (
              <div
                key={grant.id}
                className="bg-white rounded-lg shadow-sm p-6 border-l-4 border-blue-500"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <span className="bg-blue-100 text-blue-800 text-xs font-bold px-2 py-1 rounded">
                        #{index + 1}
                      </span>
                      <h3 className="text-lg font-semibold text-gray-900">{grant.name}</h3>
                    </div>

                    <p className="mt-3 text-gray-600">{grant.description}</p>

                    <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <p className="text-sm text-gray-500">Maximale Förderung</p>
                        <p className="text-xl font-bold text-gray-900">
                          {grant.max_funding.toLocaleString("de-DE")} €
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Match-Score</p>
                        <p className="text-xl font-bold text-green-600">
                          {Math.round(grant.match_score * 100)}%
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Bewilligungsquote</p>
                        <p className="text-xl font-bold text-blue-600">
                          {Math.round(grant.historical_success_rate * 100)}%
                        </p>
                      </div>
                    </div>

                    <div className="mt-4 flex items-center space-x-4 text-sm">
                      <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full">
                        {grant.type === "federal" ? "Bund" : grant.type === "state" ? "Land" : "EU"}
                      </span>
                      <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full">
                        {grant.category}
                      </span>
                      {grant.is_continuous ? (
                        <span className="text-green-600 font-medium">
                          ✓ Laufende Förderung
                        </span>
                      ) : grant.deadline ? (
                        <span className="text-orange-600 font-medium">
                          ⏰ Deadline: {new Date(grant.deadline).toLocaleDateString("de-DE")}
                        </span>
                      ) : null}
                    </div>
                  </div>
                </div>

                <div className="mt-6 flex space-x-3">
                  <button className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition">
                    Antrag starten
                  </button>
                  <button className="px-6 py-2 border border-gray-300 hover:border-gray-400 text-gray-700 rounded-lg font-medium transition">
                    Details ansehen
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {searching && (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
            <p className="text-gray-600">KI analysiert Ihr Projekt und sucht passende Förderprogramme...</p>
          </div>
        )}
      </main>
    </div>
  );
}

