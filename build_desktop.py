#!/usr/bin/env python3
"""
Build script for NanoQuant desktop applications
Creates desktop packages for macOS, Windows, and Linux using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import platform

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        print("✅ PyInstaller is already installed")
        return True
    except ImportError:
        print("📦 Installing PyInstaller...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("✅ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install PyInstaller")
            return False

def create_build_directory():
    """Create build directory for packaging"""
    build_dir = Path("build")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir()
    return build_dir

def build_macos_app():
    """Build macOS application"""
    print("🍎 Building macOS application...")
    
    try:
        # Build the app bundle
        cmd = [
            "pyinstaller",
            "--name", "NanoQuant",
            "--windowed",
            "--onedir",
            "--add-data", "nanoquant:nanoquant",
            "--hidden-import", "sklearn.utils._cython_blas",
            "--hidden-import", "sklearn.neighbors.typedefs",
            "--hidden-import", "sklearn.neighbors._typedefs",
            "nanoquant/main.py"
        ]
        
        icon_path = Path("assets/nanoquant.icns")
        if icon_path.exists():
            # Verify the icon file is valid
            try:
                from PIL import Image
                Image.open(icon_path)
                cmd.extend(["--icon", str(icon_path)])
            except Exception:
                print(f"⚠️  Invalid icon file {icon_path}, skipping icon")
        else:
            print("⚠️  Icon file not found, building without icon")
        
        subprocess.run(cmd, check=True)
        print("✅ macOS application built successfully")
        
        # Create DMG if hdiutil is available
        if shutil.which("hdiutil"):
            print("💾 Creating DMG installer...")
            try:
                subprocess.run([
                    "hdiutil", "create",
                    "-volname", "NanoQuant",
                    "-srcfolder", "dist/NanoQuant.app",
                    "-ov",
                    "-format", "UDZO",
                    "dist/NanoQuant.dmg"
                ], check=True)
                print("✅ DMG installer created successfully")
            except subprocess.CalledProcessError:
                print("⚠️  Failed to create DMG installer")
        else:
            print("ℹ️  hdiutil not available, skipping DMG creation")
            
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build macOS application: {e}")
        return False

def build_windows_app():
    """Build Windows application"""
    print("🪟 Building Windows application...")
    
    try:
        # Build the executable
        cmd = [
            "pyinstaller",
            "--name", "NanoQuant",
            "--windowed",
            "--onedir",
            "--add-data", "nanoquant;nanoquant",
            "--hidden-import", "sklearn.utils._cython_blas",
            "--hidden-import", "sklearn.neighbors.typedefs",
            "--hidden-import", "sklearn.neighbors._typedefs",
            "nanoquant/main.py"
        ]
        
        icon_path = Path("assets/nanoquant.ico")
        if icon_path.exists():
            # Verify the icon file is valid
            try:
                from PIL import Image
                Image.open(icon_path)
                cmd.extend(["--icon", str(icon_path)])
            except Exception:
                print(f"⚠️  Invalid icon file {icon_path}, skipping icon")
        else:
            print("⚠️  Icon file not found, building without icon")
        
        subprocess.run(cmd, check=True)
        print("✅ Windows application built successfully")
        
        # Create a simple installer script
        installer_script = """@echo off
echo NanoQuant Installer
echo ==================
echo Installing NanoQuant...
xcopy /E /I "NanoQuant" "%PROGRAMFILES%\\NanoQuant"
echo Creating desktop shortcut...
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = oWS.SpecialFolders("Desktop") & "\\NanoQuant.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%PROGRAMFILES%\\NanoQuant\\NanoQuant.exe" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript CreateShortcut.vbs
del CreateShortcut.vbs
echo Installation complete!
pause
"""
        
        with open("dist/install.bat", "w") as f:
            f.write(installer_script)
            
        print("✅ Windows installer script created")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build Windows application: {e}")
        return False

def build_linux_app():
    """Build Linux application"""
    print("🐧 Building Linux application...")
    
    try:
        # Build the application
        cmd = [
            "pyinstaller",
            "--name", "NanoQuant",
            "--windowed",
            "--onedir",
            "--add-data", "nanoquant:nanoquant",
            "--hidden-import", "sklearn.utils._cython_blas",
            "--hidden-import", "sklearn.neighbors.typedefs",
            "--hidden-import", "sklearn.neighbors._typedefs",
            "nanoquant/main.py"
        ]
        
        icon_path = Path("assets/nanoquant.png")
        if icon_path.exists():
            # Verify the icon file is valid
            try:
                from PIL import Image
                Image.open(icon_path)
                cmd.extend(["--icon", str(icon_path)])
            except Exception:
                print(f"⚠️  Invalid icon file {icon_path}, skipping icon")
        else:
            print("⚠️  Icon file not found, building without icon")
        
        subprocess.run(cmd, check=True)
        print("✅ Linux application built successfully")
        
        # Create AppImage if appimagetool is available
        if shutil.which("appimagetool"):
            print("💾 Creating AppImage...")
            try:
                # Create AppDir structure
                appdir = Path("dist/NanoQuant.AppDir")
                appdir.mkdir(exist_ok=True)
                
                # Copy application files
                shutil.copytree("dist/NanoQuant", appdir / "usr/bin/NanoQuant", dirs_exist_ok=True)
                
                # Create desktop entry
                desktop_content = """[Desktop Entry]
Name=NanoQuant
Exec=AppRun
Icon=nanoquant
Type=Application
Categories=Utility;
"""
                with open(appdir / "NanoQuant.desktop", "w") as f:
                    f.write(desktop_content)
                
                # Copy icon
                if Path("assets/nanoquant.png").exists():
                    shutil.copy("assets/nanoquant.png", appdir / "nanoquant.png")
                
                # Create AppRun script
                apprun_content = """#!/bin/bash
cd "$(dirname "$0")/usr/bin/NanoQuant"
./NanoQuant "$@"
"""
                with open(appdir / "AppRun", "w") as f:
                    f.write(apprun_content)
                os.chmod(appdir / "AppRun", 0o755)
                
                # Create AppImage
                subprocess.run([
                    "appimagetool", str(appdir),
                    "dist/NanoQuant.AppImage"
                ], check=True)
                print("✅ AppImage created successfully")
            except subprocess.CalledProcessError:
                print("⚠️  Failed to create AppImage")
        else:
            print("ℹ️  appimagetool not available, skipping AppImage creation")
        
        # Create Debian package structure
        print("📦 Creating Debian package structure...")
        try:
            deb_dir = Path("dist/debian")
            deb_dir.mkdir(exist_ok=True)
            
            # Create DEBIAN directory
            debian_control = deb_dir / "DEBIAN"
            debian_control.mkdir(exist_ok=True)
            
            # Create control file
            control_content = """Package: nanoquant
Version: 1.0.0
Section: utils
Priority: optional
Architecture: all
Depends: python3
Maintainer: NanoQuant Team <support@nanoquant.ai>
Description: Extreme LLM Compression Tool
 Compress large language models into extremely small versions without sacrificing quality.
"""
            with open(debian_control / "control", "w") as f:
                f.write(control_content)
            
            # Create directory structure
            usr_bin = deb_dir / "usr/bin"
            usr_bin.mkdir(parents=True, exist_ok=True)
            
            usr_share = deb_dir / "usr/share"
            usr_share.mkdir(parents=True, exist_ok=True)
            
            # Copy application files
            shutil.copytree("dist/NanoQuant", deb_dir / "usr/share/nanoquant", dirs_exist_ok=True)
            
            # Create symlink
            (usr_bin / "nanoquant").symlink_to("../share/nanoquant/NanoQuant")
            
            print("✅ Debian package structure created")
        except Exception as e:
            print(f"⚠️  Failed to create Debian package structure: {e}")
            
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build Linux application: {e}")
        return False

def main():
    """Main build function"""
    print("🚀 Starting NanoQuant desktop build process...")
    
    # Check if PyInstaller is installed
    if not check_pyinstaller():
        sys.exit(1)
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Create build directory
    build_dir = create_build_directory()
    
    # Determine which platforms to build for
    current_platform = platform.system().lower()
    print(f"🖥️  Current platform: {current_platform}")
    
    success = True
    
    # Build for current platform
    if current_platform == "darwin":  # macOS
        success = build_macos_app()
    elif current_platform == "windows":
        success = build_windows_app()
    elif current_platform == "linux":
        success = build_linux_app()
    else:
        print(f"⚠️  Unsupported platform: {current_platform}")
        success = False
    
    # If we want to build for all platforms, we would need to do cross-compilation
    # which is complex and typically done in CI/CD environments
    
    if success:
        print("\n🎉 Desktop build completed successfully!")
        print("📦 Distribution files are in the 'dist' directory")
    else:
        print("\n❌ Desktop build failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()