import Image from "next/image";
import Link from "next/link";
import { 
  Users, 
  Package, 
  TrendingUp, 
  Zap, 
  BarChart3, 
  Shield 
} from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-100 dark:from-slate-900 dark:via-slate-800 dark:to-purple-900">
      {/* Hero Section */}
      <main id="main-content" className="pt-16 pb-24">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-4xl mx-auto">
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold mb-6 leading-tight">
              <span className="text-slate-900 dark:text-white">
                Elevate Your Business{" "}
              </span>
              <span className="gradient-text">
                Management
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-slate-600 dark:text-slate-300 mb-4 leading-relaxed">
              Unified CRM and inventory platform designed for small-to-medium businesses.
            </p>
            <p className="text-lg text-slate-500 dark:text-slate-400 mb-12 leading-relaxed">
              Combine the simplicity of modern tools with enterprise-grade functionality.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
              <Link 
                href="/dashboard" 
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-1 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 min-w-[200px]"
              >
                Get Started Free
              </Link>
              <Link 
                href="/dashboard" 
                className="border-2 border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 hover:border-blue-500 dark:hover:border-blue-400 hover:text-blue-600 dark:hover:text-blue-400 px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 min-w-[200px]"
              >
                View Demo
              </Link>
            </div>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <div className="feature-card group">
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/50 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-200">
                <Users className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-slate-900 dark:text-white">Customer Management</h3>
              <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                360° customer view with communication history, preferences, and intelligent segmentation.
              </p>
            </div>

            <div className="feature-card group">
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/50 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-200">
                <Package className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-slate-900 dark:text-white">Inventory Tracking</h3>
              <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                Real-time stock tracking across warehouses with barcode scanning and automated alerts.
              </p>
            </div>

            <div className="feature-card group">
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900/50 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-200">
                <TrendingUp className="w-6 h-6 text-green-600 dark:text-green-400" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-slate-900 dark:text-white">Sales Pipeline</h3>
              <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                Visual pipeline management with automated workflows and intelligent lead scoring.
              </p>
            </div>

            <div className="feature-card group">
              <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900/50 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-200">
                <Zap className="w-6 h-6 text-orange-600 dark:text-orange-400" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-slate-900 dark:text-white">Integrations</h3>
              <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                Seamless connections to e-commerce platforms, accounting software, and productivity tools.
              </p>
            </div>

            <div className="feature-card group">
              <div className="w-12 h-12 bg-indigo-100 dark:bg-indigo-900/50 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-200">
                <BarChart3 className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-slate-900 dark:text-white">Analytics</h3>
              <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                Powerful insights with customizable dashboards and AI-powered business intelligence.
              </p>
            </div>

            <div className="feature-card group">
              <div className="w-12 h-12 bg-red-100 dark:bg-red-900/50 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-200">
                <Shield className="w-6 h-6 text-red-600 dark:text-red-400" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-slate-900 dark:text-white">Enterprise Security</h3>
              <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                Multi-factor authentication, role-based access, and GDPR compliance built-in.
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 dark:border-slate-700 bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-slate-500 dark:text-slate-400">
            <p>&copy; 2025 TECHGURU. All rights reserved. | ElevateCRM Management Tools</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
