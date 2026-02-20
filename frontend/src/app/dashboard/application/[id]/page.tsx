'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { applicationsApi, ApplicationDetail } from '@/lib/api/applications';
import { documentsApi } from '@/lib/api/documents';

export default function ApplicationDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [application, setApplication] = useState<ApplicationDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchApp = async () => {
      try {
        const data = await applicationsApi.getDetails(params.id as string);
        setApplication(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    if (params.id) fetchApp();
  }, [params.id]);

  if (loading) return <div className="min-h-screen flex items-center justify-center">Laden...</div>;
  if (!application) return <div>Nicht gefunden</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <Link href="/dashboard" className="text-blue-600 mb-4 inline-block">← Zurück</Link>
        <h1 className="text-3xl font-bold mb-4">{application.project_title}</h1>
        <p className="text-gray-600 mb-8">{application.project_description}</p>
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-bold mb-4">Budget</h2>
          <p>Gesamt: {application.total_budget.toLocaleString()} €</p>
          <p>Förderung: {application.requested_funding.toLocaleString()} €</p>
        </div>
      </div>
    </div>
  );
}
