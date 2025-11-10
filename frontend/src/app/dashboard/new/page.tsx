"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

type WizardStep = "project" | "goals" | "market" | "team" | "budget" | "review";

interface FormData {
  // Project Basics
  project_title: string;
  project_description: string;
  timeline_months: number;
  
  // Goals & Innovation
  project_goals: string[];
  innovation: string;
  technology: string;
  
  // Market & Commercialization
  target_audience: string;
  market_analysis: string;
  business_model: string;
  
  // Team & Resources
  team_info: string;
  qualifications: string;
  
  // Budget
  total_budget: number;
  requested_funding: number;
  own_contribution: number;
  budget_breakdown: {
    personnel: number;
    external: number;
    equipment: number;
    other: number;
  };
  
  // Selected grant
  grant_id: string;
}

export default function NewApplicationPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState<WizardStep>("project");
  const [formData, setFormData] = useState<FormData>({
    project_title: "",
    project_description: "",
    timeline_months: 12,
    project_goals: [""],
    innovation: "",
    technology: "",
    target_audience: "",
    market_analysis: "",
    business_model: "",
    team_info: "",
    qualifications: "",
    total_budget: 0,
    requested_funding: 0,
    own_contribution: 0,
    budget_breakdown: {
      personnel: 0,
      external: 0,
      equipment: 0,
      other: 0,
    },
    grant_id: "zim-2024-001", // TODO: Select from search
  });

  const steps: { id: WizardStep; title: string; number: number }[] = [
    { id: "project", title: "Projekt-Basics", number: 1 },
    { id: "goals", title: "Ziele & Innovation", number: 2 },
    { id: "market", title: "Markt & Verwertung", number: 3 },
    { id: "team", title: "Team & Ressourcen", number: 4 },
    { id: "budget", title: "Budget & Finanzierung", number: 5 },
    { id: "review", title: "Zusammenfassung", number: 6 },
  ];

  const currentStepIndex = steps.findIndex((s) => s.id === currentStep);
  const progress = ((currentStepIndex + 1) / steps.length) * 100;

  const handleNext = () => {
    if (currentStepIndex < steps.length - 1) {
      setCurrentStep(steps[currentStepIndex + 1].id);
    }
  };

  const handlePrevious = () => {
    if (currentStepIndex > 0) {
      setCurrentStep(steps[currentStepIndex - 1].id);
    }
  };

  const handleSubmit = async () => {
    // TODO: Call API to create application
    console.log("Submitting application:", formData);
    
    // Mock: Navigate to application page
    router.push("/dashboard/application/app-new");
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900">Neuer Förderantrag</h1>
        </div>
      </header>

      {/* Progress Bar */}
      <div className="bg-white border-b">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between mb-2">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center flex-1">
                <div
                  className={`flex items-center justify-center w-10 h-10 rounded-full font-semibold ${
                    index <= currentStepIndex
                      ? "bg-blue-600 text-white"
                      : "bg-gray-200 text-gray-600"
                  }`}
                >
                  {step.number}
                </div>
                {index < steps.length - 1 && (
                  <div
                    className={`flex-1 h-1 mx-2 ${
                      index < currentStepIndex ? "bg-blue-600" : "bg-gray-200"
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-between text-xs text-gray-600">
            {steps.map((step) => (
              <span key={step.id} className="text-center" style={{ width: `${100 / steps.length}%` }}>
                {step.title}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-sm p-8">
          {/* Step 1: Project Basics */}
          {currentStep === "project" && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900">Projekt-Basics</h2>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Projekttitel *
                </label>
                <input
                  type="text"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="z.B. AI-powered Grant Automation"
                  value={formData.project_title}
                  onChange={(e) => setFormData({ ...formData, project_title: e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Kurzbeschreibung (3-5 Sätze) *
                </label>
                <textarea
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={5}
                  placeholder="Beschreiben Sie Ihr Projekt kurz..."
                  value={formData.project_description}
                  onChange={(e) => setFormData({ ...formData, project_description: e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Projektdauer (Monate) *
                </label>
                <input
                  type="number"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={formData.timeline_months}
                  onChange={(e) => setFormData({ ...formData, timeline_months: parseInt(e.target.value) })}
                  min="1"
                  max="36"
                />
              </div>
            </div>
          )}

          {/* Step 2: Goals & Innovation */}
          {currentStep === "goals" && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900">Ziele & Innovation</h2>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Was ist neu/innovativ an Ihrem Projekt? *
                </label>
                <textarea
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={5}
                  placeholder="Beschreiben Sie den Innovationsgrad Ihres Projekts..."
                  value={formData.innovation}
                  onChange={(e) => setFormData({ ...formData, innovation: e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Welche Technologie nutzen Sie? *
                </label>
                <textarea
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={4}
                  placeholder="z.B. Python, React, AWS, Machine Learning, etc."
                  value={formData.technology}
                  onChange={(e) => setFormData({ ...formData, technology: e.target.value })}
                />
              </div>
            </div>
          )}

          {/* Step 3: Market & Commercialization */}
          {currentStep === "market" && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900">Markt & Verwertung</h2>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Wer ist Ihre Zielgruppe? *
                </label>
                <textarea
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={4}
                  placeholder="z.B. KMUs im DACH-Raum, Startups, Forschungseinrichtungen..."
                  value={formData.target_audience}
                  onChange={(e) => setFormData({ ...formData, target_audience: e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Marktgröße & Potenzial *
                </label>
                <textarea
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={4}
                  placeholder="Schätzen Sie TAM, SAM, SOM oder beschreiben Sie das Marktpotenzial..."
                  value={formData.market_analysis}
                  onChange={(e) => setFormData({ ...formData, market_analysis: e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Wie verdienen Sie Geld? (Business Model) *
                </label>
                <textarea
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={4}
                  placeholder="z.B. SaaS-Abo, Erfolgsbasiert, Freemium, etc."
                  value={formData.business_model}
                  onChange={(e) => setFormData({ ...formData, business_model: e.target.value })}
                />
              </div>
            </div>
          )}

          {/* Step 4: Team */}
          {currentStep === "team" && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900">Team & Ressourcen</h2>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Team-Zusammensetzung *
                </label>
                <textarea
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={5}
                  placeholder="z.B. 2 Senior Software Engineers, 1 Data Scientist, 1 Product Manager..."
                  value={formData.team_info}
                  onChange={(e) => setFormData({ ...formData, team_info: e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Qualifikationen & Erfahrung *
                </label>
                <textarea
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={5}
                  placeholder="Beschreiben Sie relevante Expertise, Abschlüsse, frühere Projekte..."
                  value={formData.qualifications}
                  onChange={(e) => setFormData({ ...formData, qualifications: e.target.value })}
                />
              </div>
            </div>
          )}

          {/* Step 5: Budget */}
          {currentStep === "budget" && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900">Budget & Finanzierung</h2>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Gesamtbudget (€) *
                  </label>
                  <input
                    type="number"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    value={formData.total_budget}
                    onChange={(e) => {
                      const total = parseFloat(e.target.value);
                      setFormData({ ...formData, total_budget: total });
                    }}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Fördersumme (€) *
                  </label>
                  <input
                    type="number"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    value={formData.requested_funding}
                    onChange={(e) => {
                      const requested = parseFloat(e.target.value);
                      const own = formData.total_budget - requested;
                      setFormData({ 
                        ...formData, 
                        requested_funding: requested,
                        own_contribution: own
                      });
                    }}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Eigenanteil (€)
                  </label>
                  <input
                    type="number"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50"
                    value={formData.own_contribution}
                    readOnly
                  />
                </div>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-800">
                  <strong>Tipp:</strong> Bei ZIM beträgt der Eigenanteil mindestens 15%. 
                  Ihr aktueller Eigenanteil: <strong>{formData.total_budget > 0 ? Math.round((formData.own_contribution / formData.total_budget) * 100) : 0}%</strong>
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Budget-Aufschlüsselung
                </label>
                
                <div className="space-y-3">
                  <div className="flex items-center space-x-4">
                    <label className="w-32 text-sm text-gray-700">Personal:</label>
                    <input
                      type="number"
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      value={formData.budget_breakdown.personnel}
                      onChange={(e) => setFormData({ 
                        ...formData, 
                        budget_breakdown: { ...formData.budget_breakdown, personnel: parseFloat(e.target.value) }
                      })}
                    />
                    <span className="text-gray-600">€</span>
                  </div>

                  <div className="flex items-center space-x-4">
                    <label className="w-32 text-sm text-gray-700">Externe:</label>
                    <input
                      type="number"
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      value={formData.budget_breakdown.external}
                      onChange={(e) => setFormData({ 
                        ...formData, 
                        budget_breakdown: { ...formData.budget_breakdown, external: parseFloat(e.target.value) }
                      })}
                    />
                    <span className="text-gray-600">€</span>
                  </div>

                  <div className="flex items-center space-x-4">
                    <label className="w-32 text-sm text-gray-700">Equipment:</label>
                    <input
                      type="number"
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      value={formData.budget_breakdown.equipment}
                      onChange={(e) => setFormData({ 
                        ...formData, 
                        budget_breakdown: { ...formData.budget_breakdown, equipment: parseFloat(e.target.value) }
                      })}
                    />
                    <span className="text-gray-600">€</span>
                  </div>

                  <div className="flex items-center space-x-4">
                    <label className="w-32 text-sm text-gray-700">Sonstiges:</label>
                    <input
                      type="number"
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      value={formData.budget_breakdown.other}
                      onChange={(e) => setFormData({ 
                        ...formData, 
                        budget_breakdown: { ...formData.budget_breakdown, other: parseFloat(e.target.value) }
                      })}
                    />
                    <span className="text-gray-600">€</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Step 6: Review */}
          {currentStep === "review" && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900">Zusammenfassung</h2>
              
              <div className="bg-gray-50 rounded-lg p-6 space-y-4">
                <div>
                  <h3 className="font-semibold text-gray-900">Projekttitel</h3>
                  <p className="text-gray-700">{formData.project_title}</p>
                </div>

                <div>
                  <h3 className="font-semibold text-gray-900">Beschreibung</h3>
                  <p className="text-gray-700">{formData.project_description}</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h3 className="font-semibold text-gray-900">Gesamtbudget</h3>
                    <p className="text-gray-700">{formData.total_budget.toLocaleString("de-DE")} €</p>
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">Fördersumme</h3>
                    <p className="text-gray-700">{formData.requested_funding.toLocaleString("de-DE")} €</p>
                  </div>
                </div>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h3 className="font-semibold text-blue-900 mb-2">
                  🎉 Bereit zur KI-Generierung!
                </h3>
                <p className="text-sm text-blue-800">
                  Nach dem Absenden generiert unsere KI automatisch einen vollständigen Förderantrag 
                  basierend auf Ihren Angaben. Dies dauert ca. 5-10 Minuten.
                </p>
              </div>
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="mt-8 flex justify-between">
            <button
              onClick={handlePrevious}
              disabled={currentStepIndex === 0}
              className="px-6 py-2 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              ← Zurück
            </button>

            {currentStep !== "review" ? (
              <button
                onClick={handleNext}
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition"
              >
                Weiter →
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                className="px-8 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition"
              >
                ✓ Antrag generieren
              </button>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

