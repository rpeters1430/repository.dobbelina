import os
import re
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path
from bs4 import BeautifulSoup

# Configuration
REPO_ROOT = Path(__file__).resolve().parent
IMAGES_DIR = REPO_ROOT / "plugin.video.cumination" / "resources" / "images"
SITES_DIR = REPO_ROOT / "plugin.video.cumination" / "resources" / "lib" / "sites"
TEMP_DIR = REPO_ROOT / "temp_logos"

# Ensure directories exist
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

def download_image(url, output_path):
    """Download image from URL with a common User-Agent."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            with open(output_path, 'wb') as f:
                f.write(response.read())
        return True
    except Exception as e:
        print(f"  [ERROR] Failed to download {url}: {e}")
        return False

def get_favicon_url(site_url):
    """Try to find a high-quality favicon or logo URL from a site."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        req = urllib.request.Request(site_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read()
            soup = BeautifulSoup(html, 'html.parser')
            
            # 1. Look for Apple Touch Icon (usually higher res)
            icon = soup.find('link', rel=re.compile(r'apple-touch-icon', re.I))
            if icon and icon.get('href'):
                return urllib.parse.urljoin(site_url, icon['href'])
            
            # 2. Look for shortcut icon or icon
            icon = soup.find('link', rel=re.compile(r'^(shortcut )?icon$', re.I))
            if icon and icon.get('href'):
                return urllib.parse.urljoin(site_url, icon['href'])
                
            # 3. Look for og:image
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                return urllib.parse.urljoin(site_url, og_image['content'])
    except Exception:
        pass
        
    # Fallback to standard favicon.ico
    return urllib.parse.urljoin(site_url, '/favicon.ico')

def process_logo(input_path, output_path):
    """Standardize logo using ImageMagick and pngquant."""
    try:
        # Use a temporary output path to avoid indexing issues with multi-layer/animated inputs
        base_temp_output = Path(output_path).with_name(f"temp_std_{Path(output_path).name}")
        
        # Resize to 256x256 with transparent padding
        # Use [0] to ensure we only get the first frame/layer
        cmd = [
            "magick", f"{str(input_path)}[0]",
            "-background", "none",
            "-gravity", "center",
            "-resize", "256x256",
            "-extent", "256x256",
            "-strip",
            str(base_temp_output)
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        
        # Check if it created multiple files (e.g., temp_std_logo-0.png)
        potential_files = list(base_temp_output.parent.glob(f"{base_temp_output.stem}*"))
        if not potential_files:
             # Try specifically with -0 if base didn't exist
             potential_files = list(base_temp_output.parent.glob(f"{base_temp_output.stem}-0*"))
        
        if potential_files:
            # Take the first one found
            actual_temp = potential_files[0]
            # Rename/Move to output_path
            actual_temp.replace(output_path)
            # Cleanup other potential temp files
            for f in potential_files:
                if f.exists(): f.unlink()
        else:
            return False

        # Optimize with pngquant
        try:
            subprocess.run(["pngquant", "--quality=80-95", "--ext", ".png", "--force", str(output_path)], 
                           check=True, capture_output=True)
        except Exception:
            pass # pngquant is optional
            
        return True
    except Exception as e:
        print(f"  [ERROR] ImageMagick failed for {input_path}: {e}")
        return False

def create_placeholder_logo(display_name, output_path):
    """Create a placeholder logo with the site name if all else fails."""
    try:
        # Clean up display name (remove Kodi color tags)
        clean_name = re.sub(r"\[COLOR.*?\]|\[/COLOR\]", "", display_name)
        
        # Use a temporary output path to avoid indexing issues
        base_temp_output = Path(output_path).with_name(f"temp_place_{Path(output_path).name}")

        cmd = [
            "magick",
            "-size", "256x256",
            "canvas:hotpink",
            "-fill", "white",
            "-gravity", "center",
            "-pointsize", "40",
            f"caption:{clean_name}",
            str(base_temp_output)
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        
        potential_files = list(base_temp_output.parent.glob(f"{base_temp_output.stem}*"))
        if potential_files:
            actual_temp = potential_files[0]
            actual_temp.replace(output_path)
            for f in potential_files:
                if f.exists(): f.unlink()
            return True
        return False
    except Exception as e:
        print(f"  [ERROR] Failed to create placeholder for {display_name}: {e}")
        return False

def update_site_module(site_file, old_logo, new_logo):
    """Update the logo reference in the site module."""
    content = site_file.read_text(encoding="utf-8")
    
    found = False
    for quote in ['"', "'"]:
        old_ref = f"{quote}{old_logo}{quote}"
        new_ref = f"{quote}{new_logo}{quote}"
        if old_ref in content:
            content = content.replace(old_ref, new_ref)
            found = True
            
    if found:
        site_file.write_text(content, encoding="utf-8")
        return True
    return False

def main():
    print("Auto-Adding Missing Logos...")
    
    existing_images = {f.name for f in IMAGES_DIR.iterdir() if f.is_file()}
    
    # site = AdultSite("name", "title", "url", "logo.png", ...)
    site_pattern = re.compile(r'AdultSite\s*\(\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']', re.DOTALL)
    
    found_any = False
    for site_file in SITES_DIR.glob("*.py"):
        if site_file.name in ("__init__.py", "soup_spec.py"):
            continue
            
        content = site_file.read_text(encoding="utf-8")
        match = site_pattern.search(content)
        
        if not match:
            continue
            
        site_id, display_name, base_url, logo_ref = match.groups()
        
        is_remote = logo_ref.startswith("http")
        is_missing = not is_remote and logo_ref not in existing_images
        
        if is_remote or is_missing:
            found_any = True
            print(f"\nProcessing {site_id} ({site_file.name})...")
            
            target_filename = f"{site_id}.png"
            final_path = IMAGES_DIR / target_filename
            
            success = False
            # 1. Determine source URL
            source_url = logo_ref if is_remote else get_favicon_url(base_url)
            print(f"  Attempting source URL: {source_url}")
            
            # 2. Download to temp
            parsed_url = urllib.parse.urlparse(source_url)
            temp_ext = Path(parsed_url.path).suffix or ".png"
            if temp_ext.lower() not in ('.png', '.jpg', '.jpeg', '.gif', '.ico', '.webp'):
                temp_ext = ".png"
            temp_path = TEMP_DIR / f"{site_id}_temp{temp_ext}"
            
            if download_image(source_url, temp_path):
                # 3. Process to standard PNG
                if process_logo(temp_path, final_path):
                    print(f"  Standardized logo saved to {target_filename}")
                    success = True
                
                # Cleanup temp
                if temp_path.exists():
                    temp_path.unlink()
            
            # Fallback to placeholder if failed
            if not success:
                print(f"  [INFO] Falling back to placeholder logo.")
                if create_placeholder_logo(display_name, final_path):
                    print(f"  Placeholder logo created for {site_id}")
                    success = True

            # 4. Update module if we successfully created/acquired a logo
            if success:
                if update_site_module(site_file, logo_ref, target_filename):
                    print(f"  Updated {site_file.name} to reference local logo.")
                else:
                    print(f"  [INFO] Module already references {target_filename}.")

    if not found_any:
        print("No sites with missing or remote logos found.")
    else:
        print("\nLogo automation complete.")

if __name__ == "__main__":
    main()
