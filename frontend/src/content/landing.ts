/**
 * FörderScout AI - Landing Page Content Configuration
 */

export const landingContent = {
  // Hero Section
  hero: {
    headline: "Fördermittel finden war noch nie so einfach",
    subheadline: "KI-gestützte Fördermittelsuche für Ihr Unternehmen. Wir finden passende Programme und unterstützen bei der Antragstellung.",
    cta: {
      primary: "Kostenlos starten",
      secondary: "Demo ansehen"
    },
    stats: [
      { value: "200+", label: "Förderprogramme" },
      { value: "€50Mrd", label: "Verfügbare Mittel" },
      { value: "85%", label: "Trefferquote" }
    ]
  },

  // Problem Section
  problem: {
    title: "Das Problem mit Fördermitteln",
    points: [
      {
        icon: "search",
        title: "Zu viele Programme",
        description: "Über 2.000 Förderprogramme in Deutschland – wer blickt da noch durch?"
      },
      {
        icon: "clock",
        title: "Zeitaufwändig",
        description: "Die Suche nach passenden Programmen dauert Wochen. Zeit, die Sie besser investieren könnten."
      },
      {
        icon: "document",
        title: "Komplizierte Anträge",
        description: "Antragsformulare, Nachweise, Fristen – ein Bürokratie-Dschungel."
      },
      {
        icon: "money",
        title: "Geld auf dem Tisch",
        description: "Millionen an Fördergeldern werden nicht abgerufen – weil niemand davon weiß."
      }
    ]
  },

  // Solution Section
  solution: {
    title: "So funktioniert FörderScout AI",
    steps: [
      {
        number: 1,
        title: "Profil erstellen",
        description: "Erzählen Sie uns von Ihrem Unternehmen. 5 Minuten, mehr brauchen wir nicht.",
        details: [
          "Branche & Größe",
          "Standort & Region",
          "Geplante Vorhaben"
        ]
      },
      {
        number: 2,
        title: "KI-Matching",
        description: "Unsere KI analysiert 200+ Förderprogramme und findet die besten Matches für Sie.",
        details: [
          "Automatische Analyse",
          "Relevanz-Scoring",
          "Förderchancen-Bewertung"
        ]
      },
      {
        number: 3,
        title: "Antrag stellen",
        description: "Mit unserem KI-Assistenten erstellen Sie professionelle Anträge in Stunden statt Wochen.",
        details: [
          "Vorausgefüllte Formulare",
          "Textvorschläge per KI",
          "Compliance-Check"
        ]
      },
      {
        number: 4,
        title: "Förderung erhalten",
        description: "Wir begleiten Sie bis zur Bewilligung. Sie zahlen nur bei Erfolg.",
        details: [
          "Status-Tracking",
          "Frist-Erinnerungen",
          "Erfolgs-Reporting"
        ]
      }
    ]
  },

  // Pricing Section
  pricing: {
    title: "Transparent & Fair: Sie zahlen nur bei Erfolg",
    subtitle: "Keine versteckten Kosten. Keine monatlichen Gebühren. Wir verdienen nur, wenn Sie Förderung erhalten.",
    tiers: [
      {
        name: "Success-Fee",
        price: "0€",
        period: "/ Monat",
        description: "Perfekt für den Einstieg",
        features: [
          "Unbegrenzte Programmsuche",
          "KI-Matching",
          "Basis-Antragsassistent",
          "Email-Support"
        ],
        fee: "25% bei Bewilligung",
        cta: "Kostenlos starten",
        highlighted: false
      },
      {
        name: "Hybrid",
        price: "199€",
        period: "/ Monat",
        description: "Für aktive Fördermittel-Nutzer",
        features: [
          "Alles aus Success-Fee",
          "Erweiterte KI-Funktionen",
          "Priority-Matching",
          "Telefon-Support"
        ],
        fee: "20% bei Bewilligung",
        cta: "Jetzt starten",
        highlighted: true
      },
      {
        name: "Enterprise",
        price: "499€",
        period: "/ Monat",
        description: "Für Unternehmen mit hohem Förderbedarf",
        features: [
          "Alles aus Hybrid",
          "Dedicated Account Manager",
          "White-Label Option",
          "API-Zugang",
          "Custom Integrationen"
        ],
        fee: "15% bei Bewilligung",
        cta: "Kontakt aufnehmen",
        highlighted: false
      }
    ]
  },

  // Programs Section
  programs: {
    title: "Unsere Top-Förderprogramme",
    subtitle: "Aktuell über 200 Programme für deutsche Unternehmen",
    featured: [
      {
        name: "ZIM",
        provider: "BMWK",
        maxFunding: "550.000€",
        description: "Forschung & Entwicklung für KMU",
        tags: ["Innovation", "F&E"]
      },
      {
        name: "go-digital",
        provider: "BMWK",
        maxFunding: "16.500€",
        description: "Digitalisierungsberatung für KMU",
        tags: ["Digitalisierung", "Beratung"]
      },
      {
        name: "EXIST",
        provider: "BMWK",
        maxFunding: "150.000€",
        description: "Gründerstipendium aus der Forschung",
        tags: ["Gründung", "Startup"]
      },
      {
        name: "KfW-Gründerkredit",
        provider: "KfW",
        maxFunding: "125.000€",
        description: "Günstige Kredite für Gründer",
        tags: ["Finanzierung", "Kredit"]
      },
      {
        name: "Innovationsgutschein",
        provider: "SAB Sachsen",
        maxFunding: "15.000€",
        description: "Innovation für sächsische KMU",
        tags: ["Innovation", "Sachsen"]
      },
      {
        name: "BEG Gebäudesanierung",
        provider: "BAFA",
        maxFunding: "150.000€",
        description: "Energieeffizienz für Gebäude",
        tags: ["Energie", "Sanierung"]
      }
    ]
  },

  // Testimonials
  testimonials: {
    title: "Das sagen unsere Kunden",
    items: [
      {
        quote: "Mit FörderScout haben wir in 2 Wochen 45.000€ Förderzuschuss erhalten. Alleine hätten wir Monate gebraucht.",
        author: "Michael K.",
        role: "Geschäftsführer, Softwareentwicklung",
        company: "TechStart GmbH"
      },
      {
        quote: "Endlich eine Lösung, die Fördermittel verständlich macht. Die KI-Vorschläge waren goldwert.",
        author: "Sandra M.",
        role: "Inhaberin, Handwerksbetrieb",
        company: "Elektro Meister"
      },
      {
        quote: "Der Antragsassistent hat uns Stunden an Arbeit erspart. Absolute Empfehlung!",
        author: "Thomas B.",
        role: "CFO",
        company: "InnoMed Solutions"
      }
    ]
  },

  // FAQ Section
  faq: {
    title: "Häufige Fragen",
    items: [
      {
        question: "Was kostet FörderScout?",
        answer: "Die Nutzung ist kostenlos. Wir arbeiten auf Success-Fee-Basis und erhalten nur bei erfolgreicher Bewilligung eine Provision (15-25% je nach Tarif)."
      },
      {
        question: "Welche Förderprogramme deckt ihr ab?",
        answer: "Aktuell über 200 Programme von Bund, Ländern und EU. Wir erweitern ständig und fokussieren uns auf Programme für KMU und Mittelstand."
      },
      {
        question: "Ersetzt ihr einen Förderberater?",
        answer: "FörderScout ist ein KI-gestütztes Tool, das die Suche und Antragstellung vereinfacht. Bei komplexen Fällen empfehlen wir zusätzlich einen Berater hinzuzuziehen."
      },
      {
        question: "Wie hoch ist die Erfolgsquote?",
        answer: "Unsere KI-optimierten Anträge haben eine durchschnittliche Bewilligungsquote von 70-85% – deutlich über dem Durchschnitt."
      },
      {
        question: "Handelt es sich um Rechtsberatung?",
        answer: "Nein. FörderScout bietet keine Rechtsberatung. Wir unterstützen bei der Suche und Antragstellung, aber keine rechtliche Beratung im Sinne des Rechtsberatungsgesetzes."
      },
      {
        question: "Wie sicher sind meine Daten?",
        answer: "Höchste Sicherheit: Server in Deutschland, DSGVO-konform, verschlüsselte Übertragung, keine Weitergabe an Dritte."
      }
    ]
  },

  // CTA Section
  cta: {
    title: "Bereit, Fördermittel zu finden?",
    subtitle: "Starten Sie jetzt und entdecken Sie passende Förderprogramme für Ihr Unternehmen.",
    button: "Jetzt kostenlos starten",
    note: "Keine Kreditkarte erforderlich. In 5 Minuten einsatzbereit."
  },

  // Footer
  footer: {
    company: "FörderScout AI",
    tagline: "KI-gestützte Fördermittelsuche",
    links: {
      product: [
        { label: "Funktionen", href: "/features" },
        { label: "Preise", href: "/pricing" },
        { label: "Programme", href: "/programs" },
        { label: "API", href: "/api" }
      ],
      company: [
        { label: "Über uns", href: "/about" },
        { label: "Blog", href: "/blog" },
        { label: "Karriere", href: "/jobs" },
        { label: "Kontakt", href: "/contact" }
      ],
      legal: [
        { label: "Impressum", href: "/impressum" },
        { label: "Datenschutz", href: "/datenschutz" },
        { label: "AGB", href: "/agb" }
      ],
      social: [
        { label: "LinkedIn", href: "https://linkedin.com/company/foerderscout" },
        { label: "Twitter", href: "https://twitter.com/foerderscout" }
      ]
    },
    copyright: "© 2026 FörderScout AI. Alle Rechte vorbehalten."
  }
};

export default landingContent;
