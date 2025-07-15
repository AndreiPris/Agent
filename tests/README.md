# 🧪 XOFlowers AI Agent - Test Suite

This directory contains all test files for the XOFlowers AI Agent conversational system.

## 📁 Test Files

### **test_imports.py**
- Tests all module imports and dependencies
- Ensures all components load correctly
- Useful for debugging import issues

### **test_agent.py** 
- Basic functionality test for core conversational agent components
- Tests security filters, intent classification, and action handling
- Quick validation that the system is working

### **test_enhanced_agent.py**
- Comprehensive test suite for the enhanced conversational agent
- Tests all 17 intent types with expected vs actual classification
- Provides accuracy metrics and performance analysis

## 🚀 Running Tests

### **From project root:**
```bash
# Run specific test
python tests/test_enhanced_agent.py

# Run import validation
python tests/test_imports.py

# Run basic functionality test
python tests/test_agent.py
```

### **Using pytest (if installed):**
```bash
# Install pytest
pip install pytest

# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_enhanced_agent.py -v
```

## 📊 Expected Results

### **Import Tests**
- All imports should pass with ✅ status
- No missing dependencies or module errors

### **Enhanced Agent Tests**
- **Target Accuracy:** 80%+ intent classification
- **Current Accuracy:** ~53% (needs improvement)
- **Strong Performance:** greeting, find_product, subscribe, price_inquiry
- **Needs Work:** complex queries, payment vs questions

## 🛠️ Development Workflow

1. **Make changes** to conversational agent components
2. **Run tests** to validate functionality
3. **Check accuracy** metrics for intent classification
4. **Fix issues** before committing changes
5. **Update tests** when adding new features

## 📝 Adding New Tests

When adding new functionality:

1. **Create test file** following naming convention `test_[feature].py`
2. **Add test cases** for new intent types or features
3. **Update this README** with new test descriptions
4. **Ensure tests pass** before committing

## 🎯 Test Coverage Goals

- **Intent Classification:** All 17 intent types covered
- **Security Filtering:** Malicious content detection
- **Response Generation:** All action handlers tested
- **Error Handling:** Exception scenarios covered
- **Integration:** End-to-end conversation flows

---

**Last Updated:** January 2025  
**Test Suite Version:** 1.0.0
