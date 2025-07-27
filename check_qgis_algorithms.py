# check_qgis_algorithms.py - Production-ready QGIS checker
import subprocess
import os
import platform

def get_qgis_path():
    """Get QGIS path based on environment and platform"""
    
    # Check environment variable first (for Railway/production)
    qgis_path = os.environ.get('QGIS_PATH')
    if qgis_path and os.path.exists(qgis_path):
        print(f"Using QGIS from environment variable: {qgis_path}")
        return qgis_path
    
    # Platform-specific default paths
    system = platform.system().lower()
    
    if system == "windows":
        # Common Windows QGIS paths
        possible_paths = [
            r"C:\Program Files\QGIS 3.42.3\bin\qgis_process-qgis.bat",
            r"C:\Program Files\QGIS 3.40.0\bin\qgis_process-qgis.bat",
            r"C:\Program Files\QGIS 3.38.0\bin\qgis_process-qgis.bat",
            r"C:\OSGeo4W\bin\qgis_process-qgis.bat",
            r"C:\OSGeo4W64\bin\qgis_process-qgis.bat"
        ]
    elif system == "linux":
        # Common Linux QGIS paths (for Railway/Docker)
        possible_paths = [
            "/usr/bin/qgis_process",
            "/usr/local/bin/qgis_process",
            "/opt/qgis/bin/qgis_process",
            "/usr/bin/qgis-lts",
            "/usr/bin/qgis"
        ]
    elif system == "darwin":  # macOS
        possible_paths = [
            "/Applications/QGIS.app/Contents/MacOS/bin/qgis_process",
            "/usr/local/bin/qgis_process"
        ]
    else:
        print(f"Unsupported platform: {system}")
        return None
    
    # Find first existing path
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Found QGIS at: {path}")
            return path
    
    print(f"QGIS not found on {system} platform")
    return None

def check_qgis_algorithms():
    """Check available QGIS algorithms with enhanced environment detection"""
    
    print("🔍 QGIS Algorithm Checker")
    print("=" * 40)
    
    # System information
    system_info = {
        "Platform": platform.system(),
        "Architecture": platform.machine(),
        "Python Version": platform.python_version(),
        "Environment": os.environ.get('FLASK_ENV', 'production')
    }
    
    print("System Information:")
    for key, value in system_info.items():
        print(f"  {key}: {value}")
    print()
    
    qgis_path = get_qgis_path()
    
    if not qgis_path:
        print("❌ QGIS not found on this system")
        print("\n💡 Solutions:")
        print("  1. For local development:")
        print("     - Windows: Install QGIS Desktop from qgis.org")
        print("     - Linux: sudo apt install qgis")
        print("     - macOS: brew install qgis")
        print("  2. For Railway deployment:")
        print("     - Use Docker with QGIS pre-installed")
        print("     - Set QGIS_PATH environment variable")
        print("  3. Alternative: Manual tile download is working!")
        return False
    
    try:
        print(f"✅ QGIS found at: {qgis_path}")
        print("Checking QGIS version and algorithms...")
        
        # First, try to get QGIS version
        try:
            version_result = subprocess.run([qgis_path, "--version"], 
                                          capture_output=True, text=True, timeout=30)
            if version_result.returncode == 0:
                print(f"QGIS Version: {version_result.stdout.strip()}")
        except:
            pass  # Version check is optional
        
        # List all available algorithms
        result = subprocess.run([qgis_path, "list"], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            print(f"❌ QGIS command failed: {result.stderr}")
            print(f"Return code: {result.returncode}")
            return False
        
        # Process algorithms
        lines = [line.strip() for line in result.stdout.split('\n') if line.strip()]
        
        print(f"\n📋 Total algorithms found: {len(lines)}")
        print("=" * 50)
        
        # Show first few algorithms as sample
        print("Sample algorithms:")
        for i, alg in enumerate(lines[:10]):
            print(f"  {i+1:2d}. {alg}")
        
        if len(lines) > 10:
            print(f"  ... and {len(lines) - 10} more")
        
        # Filter for tile-related algorithms
        tile_algorithms = [line for line in lines 
                          if any(keyword in line.lower() for keyword in ['tile', 'qtiles', 'xyz', 'tms', 'raster'])]
        
        print(f"\n🗂️  Tile/Raster-related algorithms ({len(tile_algorithms)} found):")
        print("=" * 50)
        
        if tile_algorithms:
            for i, alg in enumerate(tile_algorithms[:15]):  # Show first 15
                print(f"  {i+1:2d}. {alg}")
            
            if len(tile_algorithms) > 15:
                print(f"  ... and {len(tile_algorithms) - 15} more tile-related algorithms")
        else:
            print("  No tile-specific algorithms found")
        
        # Show some useful algorithms categories
        categories = {
            'Vector': ['vector', 'geometry', 'buffer', 'clip'],
            'Raster': ['raster', 'dem', 'slope', 'aspect'],
            'Processing': ['dissolve', 'merge', 'join', 'intersect'],
            'Analysis': ['distance', 'area', 'statistics', 'spatial'],
            'Export': ['export', 'save', 'write', 'output']
        }
        
        print(f"\n📊 Algorithm Categories:")
        print("=" * 30)
        for category, keywords in categories.items():
            count = sum(1 for line in lines 
                       if any(keyword in line.lower() for keyword in keywords))
            print(f"  {category:12s}: {count:3d} algorithms")
        
        print(f"\n✅ QGIS is working properly!")
        print(f"   Path: {qgis_path}")
        print(f"   Total algorithms: {len(lines)}")
        print(f"   Tile-related: {len(tile_algorithms)}")
        
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ QGIS command timed out (60 seconds)")
        print("This might indicate QGIS is installed but not working properly")
        return False
    except FileNotFoundError:
        print(f"❌ QGIS executable not found at: {qgis_path}")
        return False
    except Exception as e:
        print(f"❌ Error checking QGIS: {e}")
        print(f"Exception type: {type(e).__name__}")
        return False

def get_qgis_info():
    """Get QGIS information for Flask app integration"""
    qgis_path = get_qgis_path()
    
    info = {
        "qgis_found": qgis_path is not None,
        "qgis_path": qgis_path,
        "platform": platform.system(),
        "manual_method_available": True  # Always true - fallback method
    }
    
    if qgis_path:
        try:
            # Quick test to see if QGIS works
            result = subprocess.run([qgis_path, "list"], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                lines = [line.strip() for line in result.stdout.split('\n') if line.strip()]
                info["total_algorithms"] = len(lines)
                info["tile_algorithms"] = [line for line in lines 
                                         if any(keyword in line.lower() for keyword in ['tile', 'qtiles', 'xyz', 'tms'])][:5]
                info["qgis_working"] = True
                info["qgis_version"] = "Available"
                
                # Try to get version info
                try:
                    version_result = subprocess.run([qgis_path, "--version"], 
                                                  capture_output=True, text=True, timeout=10)
                    if version_result.returncode == 0:
                        info["qgis_version"] = version_result.stdout.strip()
                except:
                    pass  # Version is optional
                    
            else:
                info["qgis_working"] = False
                info["error"] = result.stderr or "QGIS command failed"
                
        except subprocess.TimeoutExpired:
            info["qgis_working"] = False
            info["error"] = "QGIS command timed out"
        except Exception as e:
            info["qgis_working"] = False
            info["error"] = str(e)
    
    return info

def test_qgis_algorithm(algorithm_name):
    """Test a specific QGIS algorithm"""
    qgis_path = get_qgis_path()
    
    if not qgis_path:
        return {"error": "QGIS not found"}
    
    try:
        # Get help for specific algorithm
        result = subprocess.run([qgis_path, "help", algorithm_name], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return {
                "algorithm": algorithm_name,
                "available": True,
                "help": result.stdout[:1000],  # Limit output
                "qgis_path": qgis_path
            }
        else:
            return {
                "algorithm": algorithm_name,
                "available": False,
                "error": result.stderr,
                "qgis_path": qgis_path
            }
            
    except Exception as e:
        return {
            "algorithm": algorithm_name,
            "available": False,
            "error": str(e),
            "qgis_path": qgis_path
        }

def main():
    """Main function for command line usage"""
    print("🚀 Enhanced QGIS Algorithm Checker")
    print("=" * 50)
    
    # Run the main check
    success = check_qgis_algorithms()
    
    print("\n" + "=" * 50)
    print("📊 Summary for Flask Integration:")
    print("-" * 30)
    
    # Get info for Flask app
    info = get_qgis_info()
    for key, value in info.items():
        if isinstance(value, list) and len(value) > 3:
            print(f"  {key}: {len(value)} items (showing first 3)")
            for item in value[:3]:
                print(f"    - {item}")
        else:
            print(f"  {key}: {value}")
    
    print(f"\n🔧 Environment Setup:")
    print(f"  - Set QGIS_PATH environment variable if needed")
    print(f"  - Current platform: {platform.system()}")
    print(f"  - Manual tile download: Always available")
    
    if success:
        print(f"\n✅ Ready for deployment!")
        print(f"  - QGIS integration: Working")
        print(f"  - Fallback method: Available")
    else:
        print(f"\n⚠️  Ready for deployment with limitations!")
        print(f"  - QGIS integration: Not available")
        print(f"  - Fallback method: Available (sufficient for basic usage)")
    
    return success

if __name__ == "__main__":
    main()
