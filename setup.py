from setuptools import setup, find_packages

setup(
    name="mealmatch",
    version="0.1",
    description="MealMatch CS4973 Project",
    url="https://github.com/VatsalMehta27/mealmatch",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "numpy",
        "transformers",
        "beautifulsoup4",
        "chromadb",
        "openai",
        "scikit-learn",
        "matplotlib",
        "python-dotenv",
        "gradio",
        "tqdm",
        "torch",
        "recipe-scrapers",
        "rapidfuzz",
        "requests",
        "aiohttp",
    ],
)
