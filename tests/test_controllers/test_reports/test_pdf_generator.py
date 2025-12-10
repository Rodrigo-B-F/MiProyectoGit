"""
Tests for PDF Generator
"""

import pytest
import os
from controllers import generate_purchase_report


class TestPDFGenerator:
    """Tests for PDF report generation"""
    
    def test_generate_pdf_success(self, test_db, sample_inventory, tmp_path):
        """Test successful PDF generation"""
        output_dir = str(tmp_path)
        
        pdf_path = generate_purchase_report(threshold=20, output_dir=output_dir)
        
        assert pdf_path is not None
        assert os.path.exists(pdf_path)
        assert pdf_path.endswith('.pdf')
    
    def test_generate_pdf_different_thresholds(self, test_db, sample_inventory, tmp_path):
        """Test PDF generation with different thresholds"""
        output_dir = str(tmp_path)
        
        for threshold in [10, 20, 50, 100]:
            pdf_path = generate_purchase_report(threshold=threshold, output_dir=output_dir)
            assert os.path.exists(pdf_path)
