# Frontend Integration Guide - Real-Time Data

## Quick Start

The backend now provides live, dynamic data. Update your frontend to consume these new data formats:

## 1. Getting All Crops with Real-Time Data

```javascript
// Old way (static data)
const CROPS = [ { id: 1, name: 'Paddy', msp: '₹2,183', ... } ];

// New way (dynamic data)
async function getCropsWithLiveData() {
  const response = await fetch('http://localhost:5000/api/crops');
  const data = await response.json();
  
  return {
    crops: data.crops,           // Each crop now has live MSP, diseases, stage, etc
    season: data.season,         // "Monsoon", "Summer", or "Winter"
    weather: data.weather,       // Current weather conditions
    timestamp: data.timestamp    // When data was fetched
  };
}
```

## 2. Display Live MSP on Crop Cards

```javascript
// In your crop card component
<div className="crop-card">
  <h3>{crop.name}</h3>
  <div className="msp-info">
    <span>{crop.msp}</span>
    <span className="source">{crop.msp_source}</span>
    <span className="updated">{crop.msp_updated}</span>
  </div>
  {/* Price history for chart */}
  <PriceChart data={cropDetail.price_history} />
</div>
```

## 3. Show Disease Risk Alerts

```javascript
// Disease risks are now calculated based on weather
crop.diseases.forEach(disease => {
  const riskColor = {
    'Critical': 'red',
    'Severe': 'orange',
    'High': 'amber',
    'Moderate': 'yellow',
    'Low': 'green'
  }[disease.risk_level];
  
  return (
    <Alert color={riskColor}>
      <strong>{disease.name}</strong>: {disease.risk_level}
      {disease.contributing_factors.map(f => <p>{f}</p>)}
      <em>{disease.advisory}</em>
    </Alert>
  );
});
```

## 4. Display Current Cultivation Stage

```javascript
// Show what stage the crop is currently in
<div className="cultivation-stage">
  <h4>Current Stage</h4>
  <p className="stage-name">{crop.cultivation_stage}</p>
  <p className="season">Season: {crop.cultivation_season}</p>
  <p className="timeline">
    {crop.stage_days_remaining} days remaining
  </p>
  
  <div className="operations">
    <h5>Immediate Operations</h5>
    <ul>
      {crop.immediate_operations.map(op => <li>{op}</li>)}
    </ul>
  </div>
</div>
```

## 5. Get Detailed Advisory for Specific Crop

```javascript
async function getDetailedCropAdvisory(cropId) {
  const response = await fetch(`http://localhost:5000/api/crops/${cropId}`);
  const crop = await response.json();
  
  const advisory = crop.detailed_advisory;
  
  return {
    stage: advisory.current_stage,
    season: advisory.season,
    weatherAssessment: advisory.weather_assessment,
    immediateActions: advisory.immediate_actions,      // Array of actions
    waterManagement: advisory.water_management,        // Array of tips
    nutritionTiming: advisory.nutrition_timing,        // Array of tips
    diseasePrevention: advisory.disease_prevention     // Array of measures
  };
}
```

## 6. Display Market Data with Live Pricing

```javascript
async function getMarketData(crop, region = 'Karnataka') {
  const response = await fetch('http://localhost:5000/api/market-data', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ crop, region })
  });
  
  const market = await response.json();
  
  return {
    msp: market.msp_data.msp,           // ₹2,350
    priceHistory: market.price_history, // 27 data points
    trend: market.kpis.trend,           // "Bullish", "Stable", "Bearish"
    forecast: market.kpis.forecast_percent,
    analysis: market.analysis,          // AI-generated
    updated: market.live_updated        // true/false
  };
}
```

## 7. Example: Complete Crop Knowledge Page

```javascript
import React, { useEffect, useState } from 'react';
import { AlertTriangle, TrendingUp, Sprout } from 'lucide-react';

export default function CropKnowledge({ cropId }) {
  const [crop, setCrop] = useState(null);
  const [market, setMarket] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        // Get crop detail with advisory
        const cropRes = await fetch(`http://localhost:5000/api/crops/${cropId}`);
        const cropData = await cropRes.json();
        setCrop(cropData);

        // Get market data
        const marketRes = await fetch('http://localhost:5000/api/market-data', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ crop: cropData.name, region: 'Karnataka' })
        });
        const marketData = await marketRes.json();
        setMarket(marketData);
      } catch (error) {
        console.error('Error loading data:', error);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [cropId]);

  if (loading) return <div>Loading...</div>;
  if (!crop) return <div>Crop not found</div>;

  return (
    <div className="crop-knowledge-page">
      {/* Header */}
      <div className="header">
        <img src={crop.image} alt={crop.name} />
        <div className="info">
          <h1>{crop.name}</h1>
          <p className="scientific">{crop.scientific}</p>
          <p className="region">{crop.region}</p>
        </div>
      </div>

      {/* Live Market Data */}
      <section className="market-section">
        <h2>Market Info</h2>
        <div className="msp-card">
          <h3>MSP (Live)</h3>
          <p className="price">{market.msp_data.msp}</p>
          <p className="source">{market.msp_data.source}</p>
        </div>
        <div className="trend-card">
          <h3>Trend</h3>
          <p className={`trend ${market.kpis.trend.toLowerCase()}`}>
            {market.kpis.trend} {market.kpis.trend_percent}
          </p>
        </div>
      </section>

      {/* Cultivation Stage */}
      <section className="cultivation-section">
        <h2>Current Cultivation Status</h2>
        <div className="stage-badge">{crop.cultivation_stage}</div>
        <p className="season">{crop.cultivation_season}</p>
        <div className="operations">
          <h3>Immediate Operations</h3>
          <ul>
            {crop.immediate_operations.map((op, i) => (
              <li key={i}>{op}</li>
            ))}
          </ul>
        </div>
      </section>

      {/* Disease Risks */}
      <section className="disease-section">
        <h2>Disease Monitoring</h2>
        <div className="disease-grid">
          {crop.diseases.map((disease, i) => (
            <div 
              key={i} 
              className={`disease-card risk-${disease.risk_level.toLowerCase()}`}
            >
              <h3>{disease.name}</h3>
              <p className="risk-level">{disease.risk_level}</p>
              <div className="factors">
                {disease.contributing_factors.map((f, j) => (
                  <p key={j} className="factor">{f}</p>
                ))}
              </div>
              <p className="advisory">{disease.advisory}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Detailed Advisory */}
      {crop.detailed_advisory && (
        <section className="advisory-section">
          <h2>Cultivation Advisory</h2>
          
          <div className="advisory-card">
            <h3>Weather Assessment</h3>
            <p>{crop.detailed_advisory.weather_assessment}</p>
          </div>

          <div className="advisory-card">
            <h3>Water Management</h3>
            <ul>
              {crop.detailed_advisory.water_management.map((tip, i) => (
                <li key={i}>{tip}</li>
              ))}
            </ul>
          </div>

          <div className="advisory-card">
            <h3>Nutrition Timing</h3>
            <ul>
              {crop.detailed_advisory.nutrition_timing.map((tip, i) => (
                <li key={i}>{tip}</li>
              ))}
            </ul>
          </div>

          <div className="advisory-card">
            <h3>Disease Prevention</h3>
            <ul>
              {crop.detailed_advisory.disease_prevention.map((measure, i) => (
                <li key={i}>{measure}</li>
              ))}
            </ul>
          </div>
        </section>
      )}

      {/* Timestamp */}
      <p className="timestamp">
        Data updated: {new Date(crop.timestamp).toLocaleString()}
      </p>
    </div>
  );
}
```

## 8. API Response Examples

### `/api/crops` Response Structure
```json
{
  "crops": [
    {
      "id": 1,
      "name": "Paddy",
      "scientific": "Oryza sativa",
      "variety": "Hybrid-4",
      "region": "Cauvery Basin",
      "msp": "₹2,350",
      "msp_source": "Government MSP",
      "msp_updated": "2024-12-26",
      "cycle": "120 Days",
      "water": "High",
      "yield": "25q/acre",
      "image": "https://...",
      "suitability": { ... },
      "cultivation_stage": "nursery",
      "cultivation_season": "Rabi",
      "stage_days_remaining": 45,
      "immediate_operations": [ "Seed selection", "Bed preparation", ... ],
      "diseases": [
        {
          "name": "Rice Blast",
          "risk_level": "Low",
          "risk_score": 30,
          "contributing_factors": [ "..." ],
          "advisory": "..."
        }
      ],
      "weather_context": {
        "temperature_celsius": 21,
        "humidity_percent": 51,
        "rainfall_mm": 0.5,
        "season": "Winter (Low Risk)"
      }
    }
  ],
  "season": "Winter",
  "weather": { ... },
  "timestamp": "2024-12-26T09:41:00Z",
  "data_integration": "LIVE - MSP, Weather, Disease Risk, Cultivation Stage"
}
```

### `/api/crops/1` Response Structure
```json
{
  "id": 1,
  "name": "Paddy",
  "...other fields...",
  "detailed_advisory": {
    "crop": "Paddy",
    "season": "Rabi",
    "current_stage": "nursery",
    "weather_assessment": "Temperature is optimal...",
    "immediate_actions": [ "Increase irrigation frequency...", ... ],
    "water_management": [ "Stage requirement: High (70-80% soil moisture)", ... ],
    "nutrition_timing": [ "Base fertilizer before sowing...", ... ],
    "disease_prevention": [ "Watch for damping off...", ... ]
  },
  "weather": { ... },
  "timestamp": "2024-12-26T09:41:00Z"
}
```

## 9. Styling Tips

```css
/* Risk level colors */
.risk-critical { border-left: 4px solid #dc2626; background: #fee2e2; }
.risk-severe { border-left: 4px solid #ea580c; background: #ffedd5; }
.risk-high { border-left: 4px solid #eab308; background: #fef3c7; }
.risk-moderate { border-left: 4px solid #eab308; background: #fef3c7; }
.risk-low { border-left: 4px solid #16a34a; background: #f0fdf4; }

/* Trend indicators */
.trend.bullish { color: #16a34a; }
.trend.stable { color: #6b7280; }
.trend.bearish { color: #dc2626; }
```

## 10. Error Handling

```javascript
async function safeApiCall(url, options = {}) {
  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('API call failed:', error);
    // Show fallback UI or cached data
    return null;
  }
}
```

---

**All live data is now available from the backend. Frontend integration is straightforward - just fetch and display!**
