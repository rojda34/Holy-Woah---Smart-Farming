"""
DEPRECATED: This module has been replaced by real_data_loader.py

This file previously generated synthetic datasets for model training.
It is now DISABLED in favor of loading real-world CSV data.

REASON FOR DEPRECATION:
- Synthetic data with perfect correlations no longer needed
- Real-world datasets now available in 'final dataset' folder
- Data loading is now handled by real_data_loader.py
- Eliminates data leakage from perfectly correlated synthetic features

DO NOT USE THIS MODULE - Use real_data_loader.py instead:
    from src.utils.real_data_loader import load_all_real_data
    load_all_real_data()

CRITICAL: The 25% tariff_slot noise injection is still applied during training
(see train_models.py _train_rf method for details)
"""

import logging

logger = logging.getLogger(__name__)


def generate_perfect_data():
    """
    DEPRECATED: This function is no longer used.
    
    Use real_data_loader.load_all_real_data() instead.
    Raises NotImplementedError with helpful message.
    """
    logger.error(
        "\n============════════════════════════════════════════════════════════════\n"
        "ERROR: perfect_data_generator.generate_perfect_data() is DEPRECATED\n"
        "\n"
        "Synthetic data generation has been REPLACED with real-world data loading.\n"
        "\n"
        "NEW DATA LOADING METHOD:\n"
        "    from src.utils.real_data_loader import load_all_real_data\n"
        "    load_all_real_data()\n"
        "\n"
        "TRANSITION NOTES:\n"
        "  • Real datasets are now loaded from 'final dataset' folder\n"
        "  • CSVs are processed and saved to data/processed/\n"
        "  • 25% tariff_slot noise injection STILL APPLIED during training\n"
        "  • This maintains ~88% realistic accuracy (prevents 99% leakage)\n"
        "============════════════════════════════════════════════════════════════\n"
    )
    raise NotImplementedError(
        "Synthetic data generation has been replaced with real-world data loading. "
        "Use src.utils.real_data_loader.load_all_real_data() instead."
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    generate_perfect_data()
