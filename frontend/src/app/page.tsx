'use client';

import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  const handleGetStarted = () => {
    router.push('/dashboard');
  };

  const handleLearnMore = () => {
    router.push('/grants/search');
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center">
        <h1 className="text-6xl font-bold mb-4">
          💎 GrantGPT
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Der intelligente Weg zu Fördermitteln
        </p>
        <div className="space-y-4">
          <p className="text-lg">
            <span className="font-semibold">160 Mrd. €</span> Fördermittel warten auf dich
          </p>
          <p className="text-gray-500">
            Von der Suche bis zur Bewilligung - komplett automatisiert
          </p>
        </div>
        <div className="mt-12 space-x-4">
          <button 
            onClick={handleGetStarted}
            className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition cursor-pointer"
          >
            Jetzt starten
          </button>
          <button 
            onClick={handleLearnMore}
            className="border border-gray-300 px-8 py-3 rounded-lg hover:bg-gray-50 transition cursor-pointer"
          >
            Mehr erfahren
          </button>
        </div>
        <div className="mt-16 grid grid-cols-3 gap-8">
          <div>
            <div className="text-3xl font-bold text-blue-600">2.000+</div>
            <div className="text-sm text-gray-600">Förderprogramme</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-blue-600">85%</div>
            <div className="text-sm text-gray-600">Erfolgswahrscheinlichkeit</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-blue-600">2h</div>
            <div className="text-sm text-gray-600">statt 80h Arbeit</div>
          </div>
        </div>
      </div>
    </main>
  );
}

