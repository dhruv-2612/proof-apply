from pathlib import Path
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
ROOT = Path(__file__).resolve().parents[2]
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / '.env', extra='ignore')
    app_env: str = 'development'
    llm_mode: str = 'mock'
    gemini_api_key: str = ''
    gemini_model: str = ''
    free_tier_confirmed: bool = False
    allow_paid_services: bool = False
    enable_search_grounding: bool = False
    checkpoint_backend: str = 'sqlite'
    session_ttl_minutes: int = 120
    public_live_runs: bool = False
    demo_access_code: str = ''
    data_dir: Path = ROOT / 'data'
    max_model_calls: int = 18
    max_research_calls: int = 2
    max_revisions: int = 1
    max_clarifications: int = 2
    max_active_run_seconds: int = 600
    def live_ready(self):
        import json
        try:
            report = json.loads((ROOT / 'capabilities.json').read_text())
            return bool(self.free_tier_confirmed and not self.allow_paid_services and self.gemini_api_key and self.gemini_model == report['model'] and report['structured_output'] == 'passed' and report['custom_function'] == 'passed')
        except (OSError, KeyError, ValueError): return False
    def feature_ready(self, feature):
        import json
        try:
            report = json.loads((ROOT / 'capabilities.json').read_text())
            return self.live_ready() and report.get(feature) == 'passed'
        except (OSError, ValueError): return False
settings = Settings()
# Only the workspace-local runtime; never load candidate-controlled library paths.
if os.name == 'nt':
    dlls = ROOT / '.tools/msys/ucrt64/bin'
    if dlls.exists():
        os.environ['WEASYPRINT_DLL_DIRECTORIES'] = str(dlls)

        cache = ROOT / 'tmp/fontconfig'
        cache.mkdir(parents=True, exist_ok=True)
        font_config = cache / 'fonts.conf'
        font_config.write_text('<fontconfig><dir>C:/Windows/Fonts</dir><cachedir>' + cache.as_posix() + '</cachedir></fontconfig>', encoding='utf-8')
        os.environ['FONTCONFIG_FILE'] = str(font_config)
