"""Local app test: verify refactored env handling and analyzer work."""
import sys

print("=" * 60)
print("TEST 1: Test analyzer._resolve_api_key() with env vars")
print("=" * 60)

from analyzer import _resolve_api_key, _mask_api_key

try:
    api_key, source = _resolve_api_key()
    print(f"✓ API Key Resolved")
    print(f"  Source: {source}")
    print(f"  Preview: {_mask_api_key(api_key)}")
    print(f"  Length: {len(api_key)}")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("TEST 2: Test analyzer.analyze_resume_vs_jd() function")
print("=" * 60)

from analyzer import analyze_resume_vs_jd

resume_text = """
John Doe
Senior Python Developer
Skills: Python, pandas, NumPy, Streamlit, FastAPI, Docker, AWS
Experience: 5 years in Python development, REST APIs, Data pipelines
Education: BS Computer Science
"""

job_description = """
Senior Python Engineer
Required: Python, pandas, Streamlit, REST APIs, Docker
Nice to have: AWS, kubernetes
"""

try:
    result = analyze_resume_vs_jd(resume_text, job_description)
    print(f"✓ Analysis Completed Successfully")
    print(f"  Match Score: {result.match_percentage}%")
    print(f"  Matched Skills: {result.matched_skills}")
    print(f"  Missing Skills: {result.missing_skills}")
    print(f"  Strengths: {result.strengths[:2]}")  # Show first 2
    print(f"  Improvements: {result.improvements[:2]}")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 60)
print("✓ ALL TESTS PASSED - Refactored env handling works!")
print("=" * 60)
