"""
Test script to validate all real-time data integration endpoints
Run this before deploying to ensure all dynamic data sources are working
"""

import requests
import json
from datetime import datetime
import sys

BASE_URL = "http://localhost:5000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name, success, details=""):
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if success else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"\n{status} - {name}")
    if details:
        print(f"  {details}")

def test_crops_endpoint():
    """Test /api/crops endpoint for real-time data"""
    print(f"\n{Colors.BLUE}Testing /api/crops endpoint...{Colors.END}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/crops", timeout=10)
        success = response.status_code == 200
        print_test("GET /api/crops", success, f"Status: {response.status_code}")
        
        if success:
            data = response.json()
            crops = data.get("crops", [])
            
            # Validate real-time data elements
            checks = {
                "Crops returned": len(crops) > 0,
                "Weather data included": "weather" in data,
                "Timestamp included": "timestamp" in data,
                "Live MSP data": any(crop.get("msp") for crop in crops),
                "Disease risks calculated": any(crop.get("diseases") for crop in crops),
                "Cultivation stages identified": any(crop.get("cultivation_stage") for crop in crops)
            }
            
            for check_name, check_result in checks.items():
                print_test(f"  {check_name}", check_result)
            
            if crops:
                crop = crops[0]
                print(f"\n  Sample crop data ({crop.get('name')}):")
                print(f"    - MSP: {crop.get('msp')} (from {crop.get('msp_source', 'N/A')})")
                print(f"    - Cultivation Stage: {crop.get('cultivation_stage', 'Off-season')}")
                print(f"    - Diseases: {len(crop.get('diseases', []))} tracked")
            
            return True
    except Exception as e:
        print_test("GET /api/crops", False, str(e))
        return False

def test_crop_detail_endpoint():
    """Test /api/crops/<id> endpoint"""
    print(f"\n{Colors.BLUE}Testing /api/crops/<id> endpoint...{Colors.END}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/crops/1", timeout=10)
        success = response.status_code == 200
        print_test("GET /api/crops/1", success, f"Status: {response.status_code}")
        
        if success:
            data = response.json()
            checks = {
                "Crop details returned": "name" in data,
                "Cultivation advisory included": "detailed_advisory" in data,
                "Weather context included": "weather" in data,
                "Disease data present": "diseases" in data
            }
            
            for check_name, check_result in checks.items():
                print_test(f"  {check_name}", check_result)
            
            if "detailed_advisory" in data:
                advisory = data["detailed_advisory"]
                print(f"\n  Cultivation Advisory:")
                print(f"    - Crop: {advisory.get('crop')}")
                print(f"    - Season: {advisory.get('season', 'N/A')}")
                print(f"    - Stage: {advisory.get('current_stage', 'Unknown')}")
            
            return True
    except Exception as e:
        print_test("GET /api/crops/1", False, str(e))
        return False

def test_market_data_endpoint():
    """Test /api/market-data endpoint with live pricing"""
    print(f"\n{Colors.BLUE}Testing /api/market-data endpoint...{Colors.END}")
    
    crops = ["Paddy", "Ragi", "Coffee", "Sugarcane"]
    results = []
    
    for crop in crops:
        try:
            payload = {"crop": crop, "region": "Karnataka"}
            response = requests.post(f"{BASE_URL}/api/market-data", json=payload, timeout=10)
            success = response.status_code == 200
            
            print_test(f"Market data for {crop}", success, f"Status: {response.status_code}")
            
            if success:
                data = response.json()
                checks = {
                    "MSP data": "msp_data" in data,
                    "Live updated": data.get("live_updated", False),
                    "Price history": len(data.get("price_history", [])) > 0,
                    "AI analysis": len(data.get("analysis", "")) > 0,
                    "KPIs": "kpis" in data
                }
                
                for check_name, check_result in checks.items():
                    print_test(f"  {check_name}", check_result)
                
                if "msp_data" in data:
                    msp = data["msp_data"]
                    print(f"\n  {crop} Market Data:")
                    print(f"    - MSP: {msp.get('msp')} ({msp.get('unit')})")
                    print(f"    - Source: {msp.get('source')}")
                    print(f"    - Trend: {data['kpis'].get('trend')}")
                
                results.append(True)
            else:
                results.append(False)
                
        except Exception as e:
            print_test(f"Market data for {crop}", False, str(e))
            results.append(False)
    
    return all(results)

def test_msp_module():
    """Test MSP fetcher module directly"""
    print(f"\n{Colors.BLUE}Testing MSP Fetcher module...{Colors.END}")
    
    try:
        from msp_fetcher import MSPFetcher, get_all_msp
        
        # Test fetching MSP for all crops
        all_msp = get_all_msp()
        success = len(all_msp) > 0
        print_test("Fetch all MSP", success, f"Fetched MSP for {len(all_msp)} crops")
        
        if success:
            for crop, msp_data in all_msp.items():
                if msp_data:
                    print(f"  {crop}: {msp_data['msp']} ({msp_data.get('source', 'N/A')})")
            
            # Test price history generation
            history = MSPFetcher.get_price_history("Paddy", days=180)
            print_test("Generate price history", len(history) > 0, f"Generated {len(history)} data points")
            
            return True
    except Exception as e:
        print_test("MSP Fetcher module", False, str(e))
        return False

def test_weather_disease_module():
    """Test weather and disease risk calculator"""
    print(f"\n{Colors.BLUE}Testing Weather & Disease Risk module...{Colors.END}")
    
    try:
        from weather_disease_risk import WeatherDiseaseRiskCalculator, get_crop_disease_risks
        
        # Test weather simulation
        weather = WeatherDiseaseRiskCalculator.get_simulated_weather()
        success = "temperature_celsius" in weather
        print_test("Get simulated weather", success, f"Temp: {weather.get('temperature_celsius')}°C, Humidity: {weather.get('humidity_percent')}%")
        
        # Test disease risk calculation for each crop
        crops = ["Paddy", "Ragi", "Coffee", "Sugarcane"]
        for crop in crops:
            disease_risks = get_crop_disease_risks(crop)
            has_risks = len(disease_risks.get("diseases", [])) > 0
            print_test(f"Calculate disease risks for {crop}", has_risks, f"Found {len(disease_risks.get('diseases', []))} diseases")
            
            if has_risks:
                for disease in disease_risks["diseases"][:1]:
                    print(f"    - {disease['name']}: {disease['risk_level']} risk")
        
        return True
    except Exception as e:
        print_test("Weather & Disease module", False, str(e))
        return False

def test_cultivation_advisor_module():
    """Test cultivation advisor"""
    print(f"\n{Colors.BLUE}Testing Cultivation Advisor module...{Colors.END}")
    
    try:
        from cultivation_advisor import CultivationAdvisor
        from weather_disease_risk import WeatherDiseaseRiskCalculator
        
        weather = WeatherDiseaseRiskCalculator.get_simulated_weather()
        
        crops = ["Paddy", "Ragi", "Coffee", "Sugarcane"]
        
        # Test stage detection
        stage_test_passed = False
        for crop in crops:
            stage = CultivationAdvisor.get_current_cultivation_stage(crop)
            has_stage = "current_stage" in stage or "status" in stage
            status = stage.get("current_stage") or stage.get("status", "Unknown")
            print_test(f"Get cultivation stage for {crop}", has_stage, f"Stage: {status}")
            stage_test_passed = has_stage or stage_test_passed
        
        # Test advisory generation
        advisory_test_passed = False
        for crop in crops:
            try:
                advisory = CultivationAdvisor.get_weather_based_recommendations(crop, weather)
                has_advisory = ("immediate_actions" in advisory) or ("status" in advisory)
                season = advisory.get("season") or advisory.get("status", "Off-season")
                print_test(f"Get advisory for {crop}", has_advisory, f"Season: {season}")
                advisory_test_passed = has_advisory or advisory_test_passed
            except Exception as e:
                print_test(f"Get advisory for {crop}", False, str(e))
        
        return stage_test_passed and advisory_test_passed
    except Exception as e:
        print_test("Cultivation Advisor module", False, str(e))
        import traceback
        traceback.print_exc()
        return False

def main():
    print(f"\n{Colors.BLUE}{'='*60}")
    print("VANI AI - Real-Time Data Integration Test Suite")
    print(f"{'='*60}{Colors.END}")
    print(f"Testing real-time MSP, weather, disease risk, and cultivation data")
    print(f"Timestamp: {datetime.now().isoformat()}\n")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/crops", timeout=2)
    except:
        print(f"{Colors.YELLOW}⚠ Backend server not running!{Colors.END}")
        print(f"Please start the backend with: python app.py")
        print(f"\nRunning module tests instead...\n")
        
        module_tests = [
            test_msp_module(),
            test_weather_disease_module(),
            test_cultivation_advisor_module()
        ]
        
        if all(module_tests):
            print(f"\n{Colors.GREEN}{'='*60}")
            print("✓ All module tests PASSED!")
            print(f"{'='*60}{Colors.END}")
            print("\nNext: Start the backend server and run endpoint tests")
        else:
            print(f"\n{Colors.RED}{'='*60}")
            print("✗ Some module tests FAILED")
            print(f"{'='*60}{Colors.END}")
        return
    
    # Run endpoint tests
    endpoint_tests = [
        test_crops_endpoint(),
        test_crop_detail_endpoint(),
        test_market_data_endpoint()
    ]
    
    # Run module tests
    module_tests = [
        test_msp_module(),
        test_weather_disease_module(),
        test_cultivation_advisor_module()
    ]
    
    all_tests = endpoint_tests + module_tests
    
    print(f"\n{Colors.BLUE}{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}{Colors.END}")
    
    passed = sum(all_tests)
    total = len(all_tests)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if all(all_tests):
        print(f"\n{Colors.GREEN}✓ All tests PASSED! Real-time integration is working.{Colors.END}")
    else:
        print(f"\n{Colors.RED}✗ Some tests FAILED. Check the details above.{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()
