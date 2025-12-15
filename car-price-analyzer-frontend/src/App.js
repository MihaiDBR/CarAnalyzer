import React, { useState } from 'react';
import { Car, TrendingUp, TrendingDown, DollarSign, Search, CheckCircle, BarChart3, Clock, RefreshCw, Download } from 'lucide-react';
import { analyzePrice } from './services/api';

function App() {
  const [carData, setCarData] = useState({
    marca: '',
    model: '',
    an: '',
    km: '',
    combustibil: 'benzina',
    dotari: [],
    locatie: 'bucuresti'
  });
  
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const dotariDisponibile = [
    { id: 'piele', nume: 'Interior piele' },
    { id: 'navigatie', nume: 'Sistem navigație' },
    { id: 'xenon', nume: 'Faruri Xenon/LED' },
    { id: 'senzori', nume: 'Senzori parcare' },
    { id: 'camera', nume: 'Cameră marsarier' },
    { id: 'scaune', nume: 'Scaune încălzite' },
    { id: 'clima', nume: 'Climatronic' },
    { id: 'jante', nume: 'Jante aliaj' },
    { id: 'cruise', nume: 'Cruise control' },
    { id: 'keyless', nume: 'Keyless entry' },
    { id: 'trapa', nume: 'Trapă panoramic' },
    { id: 'sport', nume: 'Pachet sport' }
  ];

  const marci = ['Volkswagen', 'BMW', 'Mercedes', 'Audi', 'Skoda', 'Dacia', 'Ford', 'Opel', 'Toyota', 'Honda', 'Mazda'];
  const locatii = ['bucuresti', 'cluj', 'timisoara', 'iasi', 'constanta', 'brasov'];

  const handleDotareToggle = (dotareId) => {
    setCarData(prev => ({
      ...prev,
      dotari: prev.dotari.includes(dotareId)
        ? prev.dotari.filter(d => d !== dotareId)
        : [...prev.dotari, dotareId]
    }));
  };

  const analyzeCarPrice = async () => {
    if (!carData.marca || !carData.model || !carData.an || !carData.km) {
      setError('Te rog completează toate câmpurile obligatorii!');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const result = await analyzePrice(carData);
      
      setAnalysis({
        pricing: {
          pretRapid: result.pret_rapid,
          pretOptim: result.pret_optim,
          pretNegociere: result.pret_negociere,
          pretMaxim: result.pret_maxim
        },
        valoreDotari: result.valoare_dotari,
        marketData: result.market_data
      });
      
    } catch (error) {
      console.error('Eroare:', error);
      setError('Eroare la analiză: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const exportData = () => {
    if (!analysis) return;
    
    const exportObj = {
      masina: carData,
      analiza: analysis,
      data: new Date().toISOString()
    };
    
    const dataStr = JSON.stringify(exportObj, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `analiza-${carData.marca}-${carData.model}-${Date.now()}.json`;
    link.click();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-4 md:p-6">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Car className="w-12 h-12 text-indigo-600" />
            <h1 className="text-3xl md:text-4xl font-bold text-gray-800">Analizor Preț Mașini</h1>
          </div>
          <p className="text-gray-600">Analiză profesională bazată pe date reale din piață</p>
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-6 text-gray-800">Date Mașină</h2>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Marcă *</label>
                  <select
                    value={carData.marca}
                    onChange={(e) => setCarData({...carData, marca: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="">Selectează</option>
                    {marci.map(marca => (
                      <option key={marca} value={marca}>{marca}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Model *</label>
                  <input
                    type="text"
                    value={carData.model}
                    onChange={(e) => setCarData({...carData, model: e.target.value})}
                    placeholder="Golf, Seria 3"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">An *</label>
                  <input
                    type="number"
                    value={carData.an}
                    onChange={(e) => setCarData({...carData, an: e.target.value})}
                    placeholder="2020"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Kilometri *</label>
                  <input
                    type="number"
                    value={carData.km}
                    onChange={(e) => setCarData({...carData, km: e.target.value})}
                    placeholder="100000"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Locație</label>
                  <select
                    value={carData.locatie}
                    onChange={(e) => setCarData({...carData, locatie: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  >
                    {locatii.map(loc => (
                      <option key={loc} value={loc}>{loc.charAt(0).toUpperCase() + loc.slice(1)}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Combustibil</label>
                <select
                  value={carData.combustibil}
                  onChange={(e) => setCarData({...carData, combustibil: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="benzina">Benzină</option>
                  <option value="diesel">Diesel</option>
                  <option value="electric">Electric</option>
                  <option value="hybrid">Hybrid</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Dotări opționale ({carData.dotari.length} selectate)
                </label>
                <div className="grid grid-cols-2 gap-2 max-h-64 overflow-y-auto bg-gray-50 p-3 rounded-lg">
                  {dotariDisponibile.map(dotare => (
                    <label
                      key={dotare.id}
                      className="flex items-center gap-2 p-2 rounded hover:bg-white cursor-pointer transition"
                    >
                      <input
                        type="checkbox"
                        checked={carData.dotari.includes(dotare.id)}
                        onChange={() => handleDotareToggle(dotare.id)}
                        className="w-4 h-4 text-indigo-600 rounded"
                      />
                      <span className="text-sm text-gray-700">{dotare.nume}</span>
                    </label>
                  ))}
                </div>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                  {error}
                </div>
              )}

              <button
                onClick={analyzeCarPrice}
                disabled={loading}
                className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold py-3 px-6 rounded-lg transition flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <RefreshCw className="w-5 h-5 animate-spin" />
                    <span>Se analizează...</span>
                  </>
                ) : (
                  <>
                    <Search className="w-5 h-5" />
                    <span>Analizează Prețul</span>
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-semibold text-gray-800">Rezultate Analiză</h2>
              {analysis && (
                <button
                  onClick={exportData}
                  className="flex items-center gap-2 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition text-sm"
                >
                  <Download className="w-4 h-4" />
                  Export
                </button>
              )}
            </div>
            
            {!analysis ? (
              <div className="flex flex-col items-center justify-center h-96 text-gray-400">
                <DollarSign className="w-20 h-20 mb-4" />
                <p className="text-center">Completează datele și analizează<br/>pentru recomandări personalizate</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="bg-gradient-to-r from-red-50 to-orange-50 border-2 border-red-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <TrendingDown className="w-5 h-5 text-red-600" />
                      <h3 className="font-semibold text-red-800">Vânzare Rapidă</h3>
                    </div>
                    <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded-full">
                      {analysis.pricing.pretRapid.probabilitate}% șansă
                    </span>
                  </div>
                  <div className="text-3xl font-bold text-red-600 mb-1">
                    €{Math.round(analysis.pricing.pretRapid.valoare).toLocaleString()}
                  </div>
                  <p className="text-sm text-red-700">{analysis.pricing.pretRapid.timp}</p>
                </div>

                <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-300 rounded-lg p-4 ring-2 ring-green-400">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-5 h-5 text-green-600" />
                      <h3 className="font-semibold text-green-800">Preț Optim ⭐</h3>
                    </div>
                    <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
                      {analysis.pricing.pretOptim.probabilitate}% șansă
                    </span>
                  </div>
                  <div className="text-3xl font-bold text-green-600 mb-1">
                    €{Math.round(analysis.pricing.pretOptim.valoare).toLocaleString()}
                  </div>
                  <p className="text-sm text-green-700">{analysis.pricing.pretOptim.timp}</p>
                </div>

                <div className="bg-gradient-to-r from-blue-50 to-cyan-50 border-2 border-blue-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Clock className="w-5 h-5 text-blue-600" />
                      <h3 className="font-semibold text-blue-800">Cu Spațiu Negociere</h3>
                    </div>
                    <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
                      {analysis.pricing.pretNegociere.probabilitate}% șansă
                    </span>
                  </div>
                  <div className="text-3xl font-bold text-blue-600 mb-1">
                    €{Math.round(analysis.pricing.pretNegociere.valoare).toLocaleString()}
                  </div>
                  <p className="text-sm text-blue-700">{analysis.pricing.pretNegociere.timp}</p>
                </div>

                <div className="bg-gradient-to-r from-purple-50 to-pink-50 border-2 border-purple-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="w-5 h-5 text-purple-600" />
                      <h3 className="font-semibold text-purple-800">Preț Premium</h3>
                    </div>
                    <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">
                      {analysis.pricing.pretMaxim.probabilitate}% șansă
                    </span>
                  </div>
                  <div className="text-3xl font-bold text-purple-600 mb-1">
                    €{Math.round(analysis.pricing.pretMaxim.valoare).toLocaleString()}
                  </div>
                  <p className="text-sm text-purple-700">{analysis.pricing.pretMaxim.timp}</p>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                    <BarChart3 className="w-5 h-5" />
                    Date Piață
                  </h3>
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <span className="text-gray-600">Valoare dotări:</span>
                      <span className="font-semibold text-gray-800 ml-2">€{Math.round(analysis.valoreDotari).toLocaleString()}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Total anunțuri:</span>
                      <span className="font-semibold text-gray-800 ml-2">{analysis.marketData.total_listings}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Preț median:</span>
                      <span className="font-semibold text-gray-800 ml-2">€{Math.round(analysis.marketData.price_median).toLocaleString()}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Range piață:</span>
                      <span className="font-semibold text-gray-800 ml-2">
                        €{Math.round(analysis.marketData.price_min).toLocaleString()} - €{Math.round(analysis.marketData.price_max).toLocaleString()}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;