import React, { useState } from 'react';
import { QueryInterface } from './components/QueryInterface';
import { ResultDisplay } from './components/ResultDisplay';
import { SystemStats } from './components/SystemStats';
import { QueryResponse } from './types';

function App() {
  const [queryResult, setQueryResult] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const handleQueryResult = (result: QueryResponse) => {
    setQueryResult(result);
  };

  const handleLoading = (isLoading: boolean) => {
    setLoading(isLoading);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">AI</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  Australian Immigration Law RAG
                </h1>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Query Interface + Chat */}
          <div className="lg:col-span-2">
            <QueryInterface
              queryResult={queryResult}
              loading={loading}
              onQueryResult={handleQueryResult}
              onLoading={handleLoading}
            />
          </div>

          {/* Right Column - System Stats */}
          <div className="lg:col-span-1">
            <SystemStats />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-sm text-gray-600">
            <p>
              This system demonstrates sovereign AI capabilities for Australian immigration law.
              Built with gpt-oss-20b, ChromaDB, and FastAPI.
            </p>
            <p className="mt-2">
              Upload your own immigration law documents to expand the knowledge base.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;

