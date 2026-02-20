import Link from 'next/link';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-900 text-gray-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Company Info */}
          <div className="col-span-1">
            <h3 className="text-white text-lg font-bold mb-4">FörderScout AI</h3>
            <p className="text-sm text-gray-400">
              Intelligente Fördermittelsuche und Antragsassistenz für deutsche Unternehmen.
            </p>
          </div>

          {/* Product */}
          <div>
            <h4 className="text-white text-sm font-semibold mb-4">Produkt</h4>
            <ul className="space-y-2">
              <li>
                <Link href="/grants/search" className="text-sm hover:text-white transition-colors">
                  Förderprogramme
                </Link>
              </li>
              <li>
                <Link href="/dashboard" className="text-sm hover:text-white transition-colors">
                  Dashboard
                </Link>
              </li>
              <li>
                <Link href="/pricing" className="text-sm hover:text-white transition-colors">
                  Preise
                </Link>
              </li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h4 className="text-white text-sm font-semibold mb-4">Unternehmen</h4>
            <ul className="space-y-2">
              <li>
                <Link href="/about" className="text-sm hover:text-white transition-colors">
                  Über uns
                </Link>
              </li>
              <li>
                <Link href="/contact" className="text-sm hover:text-white transition-colors">
                  Kontakt
                </Link>
              </li>
              <li>
                <Link href="/blog" className="text-sm hover:text-white transition-colors">
                  Blog
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className="text-white text-sm font-semibold mb-4">Rechtliches</h4>
            <ul className="space-y-2">
              <li>
                <Link href="/imprint" className="text-sm hover:text-white transition-colors">
                  Impressum
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="text-sm hover:text-white transition-colors">
                  Datenschutz
                </Link>
              </li>
              <li>
                <Link href="/terms" className="text-sm hover:text-white transition-colors">
                  AGB
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-gray-800">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-sm text-gray-400">
              © {currentYear} FörderScout AI. Alle Rechte vorbehalten.
            </p>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <a
                href="https://twitter.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-white transition-colors"
              >
                <span className="sr-only">Twitter</span>
                <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
                </svg>
              </a>
              <a
                href="https://linkedin.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-white transition-colors"
              >
                <span className="sr-only">LinkedIn</span>
                <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" />
                </svg>
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
