import React, { useState, useEffect } from 'react';
import { Car, TrendingUp, TrendingDown, DollarSign, Search, CheckCircle, BarChart3, Clock, RefreshCw, Download } from 'lucide-react';
import { analyzePrice, fetchCatalogBrands, fetchCatalogModels } from './services/api';

function App() {
  const [carData, setCarData] = useState({
    marca: '',
    model: '',
    an: '',
    km: '',
    combustibil: 'benzina',
    transmisie: '',
    tractiune: '',
    caroserie: ''
  });

  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Dynamic catalog data
  const [brands, setBrands] = useState([]);
  const [modelSeries, setModelSeries] = useState([]);
  const [loadingBrands, setLoadingBrands] = useState(false);
  const [loadingModels, setLoadingModels] = useState(false);

  // Fetch brands on component mount
  useEffect(() => {
    loadBrands();
  }, []);

  // Fetch model series when brand changes
  useEffect(() => {
    if (carData.marca) {
      loadModelSeries(carData.marca);
    } else {
      setModelSeries([]);
      setCarData(prev => ({ ...prev, model: '' }));
    }
  }, [carData.marca]);

  const loadBrands = async () => {
    setLoadingBrands(true);
    try {
      const brandsData = await fetchCatalogBrands();
      setBrands(brandsData);
    } catch (error) {
      console.error('Error loading brands:', error);
      setError('Eroare la încărcarea mărcilor. Încearcă din nou.');
    } finally {
      setLoadingBrands(false);
    }
  };

  const loadModelSeries = async (marca) => {
    setLoadingModels(true);
    try {
      const modelsData = await fetchCatalogModels(marca);
      setModelSeries(modelsData);
    } catch (error) {
      console.error('Error loading models:', error);
      setModelSeries([]);
    } finally {
      setLoadingModels(false);
    }
  };

  const handleBrandChange = (brand) => {
    setCarData(prev => ({
      ...prev,
      marca: brand,
      model: ''
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
          <p className="text-gray-600">Analiză profesională bazată pe date reale din piața OLX</p>
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-6 text-gray-800">Date Mașină</h2>

            <div className="space-y-4">
              {/* Brand and Model Selection */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Marcă * {loadingBrands && <span className="text-xs text-gray-500">(se încarcă...)</span>}
                  </label>
                  <select
                    value={carData.marca}
                    onChange={(e) => handleBrandChange(e.target.value)}
                    disabled={loadingBrands}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-100"
                  >
                    <option value="">Selectează marca</option>
                    {brands.map(brand => (
                      <option key={brand.value} value={brand.value}>
                        {brand.label}
                        {brand.isTop ? ' ⭐' : ''}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Model * {loadingModels && <span className="text-xs text-gray-500">(se încarcă...)</span>}
                  </label>
                  <select
                    value={carData.model}
                    onChange={(e) => setCarData({...carData, model: e.target.value})}
                    disabled={!carData.marca || loadingModels}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-100"
                  >
                    <option value="">
                      {!carData.marca ? 'Selectează mai întâi marca' : 'Selectează modelul'}
                    </option>
                    {modelSeries.map(series => (
                      <option key={series.series} value={series.series}>
                        {series.series}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Year and KM */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">An *</label>
                  <input
                    type="number"
                    value={carData.an}
                    onChange={(e) => setCarData({...carData, an: e.target.value})}
                    placeholder="2020"
                    min="1990"
                    max="2025"
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
                    min="0"
                    max="1000000"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>

              {/* Fuel Type and Transmission */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Combustibil *</label>
                  <select
                    value={carData.combustibil}
                    onChange={(e) => setCarData({...carData, combustibil: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="benzina">Benzină</option>
                    <option value="diesel">Diesel</option>
                    <option value="electric">Electric</option>
                    <option value="hybrid">Hybrid</option>
                    <option value="gpl">GPL</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Transmisie</label>
                  <select
                    value={carData.transmisie}
                    onChange={(e) => setCarData({...carData, transmisie: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="">Toate</option>
                    <option value="manuala">Manuală</option>
                    <option value="automata">Automată</option>
                  </select>
                </div>
              </div>

              {/* Body Type and Drivetrain */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Caroserie</label>
                  <select
                    value={carData.caroserie}
                    onChange={(e) => setCarData({...carData, caroserie: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="">Toate</option>
                    <option value="sedan">Sedan</option>
                    <option value="hatchback">Hatchback</option>
                    <option value="break">Break</option>
                    <option value="suv">SUV</option>
                    <option value="coupe">Coupe</option>
                    <option value="cabrio">Cabrio</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Tracțiune</label>
                  <select
                    value={carData.tractiune}
                    onChange={(e) => setCarData({...carData, tractiune: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="">Toate</option>
                    <option value="fata">Față</option>
                    <option value="spate">Spate</option>
                    <option value="4x4">4x4 (AWD)</option>
                  </select>
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
                    <span>Se analizează... (poate dura 10-30s)</span>
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
                <p className="text-center">Completează datele și analizează<br/>pentru recomandări personalizate din piața reală</p>
                <p className="text-xs text-center mt-4 text-gray-500">Prima analiză poate dura mai mult (10-30s)<br/>pentru că se face scraping automat pe OLX</p>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Market Data Info Box */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
                  <div className="flex items-start gap-2">
                    <BarChart3 className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                    <div className="text-sm">
                      <p className="font-semibold text-blue-900 mb-1">
                        {analysis.marketData.description}
                      </p>
                      <p className="text-blue-700">
                        Încredere: {analysis.marketData.confidence}% •
                        Anunțuri: {analysis.marketData.sample_size}
                      </p>
                    </div>
                  </div>
                </div>

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
                  <p className="text-xs text-red-600 mt-1">{analysis.pricing.pretRapid.descriere}</p>
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
                  <p className="text-xs text-green-600 mt-1">{analysis.pricing.pretOptim.descriere}</p>
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
                  <p className="text-xs text-blue-600 mt-1">{analysis.pricing.pretNegociere.descriere}</p>
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
                  <p className="text-xs text-purple-600 mt-1">{analysis.pricing.pretMaxim.descriere}</p>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                    <BarChart3 className="w-5 h-5" />
                    Statistici Piață
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
                    {analysis.marketData.price_median > 0 && (
                      <>
                        <div>
                          <span className="text-gray-600">Preț median:</span>
                          <span className="font-semibold text-gray-800 ml-2">€{Math.round(analysis.marketData.price_median).toLocaleString()}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Preț mediu:</span>
                          <span className="font-semibold text-gray-800 ml-2">€{Math.round(analysis.marketData.price_mean).toLocaleString()}</span>
                        </div>
                      </>
                    )}
                    {analysis.marketData.price_min > 0 && analysis.marketData.price_max > 0 && (
                      <div className="col-span-2">
                        <span className="text-gray-600">Range piață:</span>
                        <span className="font-semibold text-gray-800 ml-2">
                          €{Math.round(analysis.marketData.price_min).toLocaleString()} - €{Math.round(analysis.marketData.price_max).toLocaleString()}
                        </span>
                      </div>
                    )}
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
