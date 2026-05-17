/**
 * AI Growth Labs — Form Validation & Rate Limiting
 * - International phone number validation (country-specific digit counts)
 * - Email validation (format + disposable domain blocking)
 * - Rate limiting: max 3 submissions per form per 24 hours (per browser)
 */

(function() {
  'use strict';

  // Country phone formats: [country code prefix, min digits, max digits, display name]
  var PHONE_FORMATS = [
    { prefix: '+1',   digits: [10, 10], name: 'USA/Canada',    placeholder: '+1 (555) 123-4567' },
    { prefix: '+44',  digits: [10, 10], name: 'UK',            placeholder: '+44 7XXX XXXXXX' },
    { prefix: '+91',  digits: [10, 10], name: 'India',         placeholder: '+91 9XXX XXXXXX' },
    { prefix: '+61',  digits: [9, 9],   name: 'Australia',     placeholder: '+61 4XX XXX XXX' },
    { prefix: '+49',  digits: [10, 11], name: 'Germany',       placeholder: '+49 XXX XXXXXXXX' },
    { prefix: '+33',  digits: [9, 9],   name: 'France',        placeholder: '+33 X XX XX XX XX' },
    { prefix: '+971', digits: [9, 9],   name: 'UAE',           placeholder: '+971 5X XXX XXXX' },
    { prefix: '+966', digits: [9, 9],   name: 'Saudi Arabia',  placeholder: '+966 5X XXX XXXX' },
    { prefix: '+55',  digits: [10, 11], name: 'Brazil',        placeholder: '+55 XX XXXXX XXXX' },
    { prefix: '+81',  digits: [10, 10], name: 'Japan',         placeholder: '+81 X0 XXXX XXXX' },
    { prefix: '+86',  digits: [11, 11], name: 'China',         placeholder: '+86 1XX XXXX XXXX' },
    { prefix: '+82',  digits: [10, 11], name: 'South Korea',   placeholder: '+82 10 XXXX XXXX' },
    { prefix: '+234', digits: [10, 10], name: 'Nigeria',       placeholder: '+234 8XX XXX XXXX' },
    { prefix: '+27',  digits: [9, 9],   name: 'South Africa',  placeholder: '+27 XX XXX XXXX' },
    { prefix: '+52',  digits: [10, 10], name: 'Mexico',        placeholder: '+52 XX XXXX XXXX' },
    { prefix: '+39',  digits: [9, 10],  name: 'Italy',         placeholder: '+39 XXX XXX XXXX' },
    { prefix: '+34',  digits: [9, 9],   name: 'Spain',         placeholder: '+34 XXX XXX XXX' },
    { prefix: '+7',   digits: [10, 10], name: 'Russia',        placeholder: '+7 XXX XXX XXXX' },
    { prefix: '+90',  digits: [10, 10], name: 'Turkey',        placeholder: '+90 5XX XXX XXXX' },
    { prefix: '+62',  digits: [10, 12], name: 'Indonesia',     placeholder: '+62 8XX XXXX XXXX' },
    { prefix: '+63',  digits: [10, 10], name: 'Philippines',   placeholder: '+63 9XX XXX XXXX' },
    { prefix: '+20',  digits: [10, 10], name: 'Egypt',         placeholder: '+20 1X XXXX XXXX' },
    { prefix: '+48',  digits: [9, 9],   name: 'Poland',        placeholder: '+48 XXX XXX XXX' },
    { prefix: '+31',  digits: [9, 9],   name: 'Netherlands',   placeholder: '+31 6 XXXX XXXX' },
    { prefix: '+60',  digits: [9, 10],  name: 'Malaysia',      placeholder: '+60 1X XXX XXXX' },
    { prefix: '+65',  digits: [8, 8],   name: 'Singapore',     placeholder: '+65 XXXX XXXX' },
    { prefix: '+94',  digits: [9, 9],   name: 'Sri Lanka',     placeholder: '+94 7X XXX XXXX' },
    { prefix: '+880', digits: [10, 10], name: 'Bangladesh',    placeholder: '+880 1XXX XXXXXX' }
  ];

  // Sort by prefix length descending so longer prefixes match first
  PHONE_FORMATS.sort(function(a, b) { return b.prefix.length - a.prefix.length; });

  // Disposable email domains to block
  var DISPOSABLE_DOMAINS = [
    'tempmail.com', 'throwaway.email', 'guerrillamail.com', 'mailinator.com',
    'trashmail.com', 'yopmail.com', 'sharklasers.com', 'guerrillamail.info',
    'grr.la', 'tempail.com', 'temp-mail.org', 'fakeinbox.com',
    'maildrop.cc', 'dispostable.com', '10minutemail.com', 'getnada.com'
  ];

  // ========== PHONE VALIDATION ==========
  function validatePhone(phone) {
    if (!phone) return { valid: false, error: 'Phone number is required.' };

    // Strip all non-digit characters except leading +
    var cleaned = phone.replace(/[^\d+]/g, '');
    
    // If no + prefix, try to detect
    if (cleaned.charAt(0) !== '+') {
      // If starts with 0, it's a local number — we can't validate without country
      if (cleaned.charAt(0) === '0') {
        // Assume US if 10 digits starting with 0 removed
        var withoutZero = cleaned.substring(1);
        if (withoutZero.length >= 7 && withoutZero.length <= 12) {
          return { valid: true };
        }
        return { valid: false, error: 'Please include your country code (e.g., +971 for UAE, +1 for USA, +44 for UK).' };
      }
      // Could be US number without +1
      if (cleaned.length === 10) {
        return { valid: true };
      }
      if (cleaned.length === 11 && cleaned.charAt(0) === '1') {
        return { valid: true };
      }
      return { valid: false, error: 'Please include your country code (e.g., +971 for UAE, +1 for USA, +44 for UK).' };
    }

    // Has + prefix — match against known formats
    var digitsOnly = cleaned.replace('+', '');
    
    for (var i = 0; i < PHONE_FORMATS.length; i++) {
      var fmt = PHONE_FORMATS[i];
      var prefixDigits = fmt.prefix.replace('+', '');
      
      if (digitsOnly.indexOf(prefixDigits) === 0) {
        var numberPart = digitsOnly.substring(prefixDigits.length);
        var minDigits = fmt.digits[0];
        var maxDigits = fmt.digits[1];
        
        if (numberPart.length < minDigits) {
          return { 
            valid: false, 
            error: 'Phone number too short for ' + fmt.name + '. Expected ' + (minDigits + prefixDigits.length) + ' digits total (format: ' + fmt.placeholder + ').' 
          };
        }
        if (numberPart.length > maxDigits) {
          return { 
            valid: false, 
            error: 'Phone number too long for ' + fmt.name + '. Expected ' + (maxDigits + prefixDigits.length) + ' digits total (format: ' + fmt.placeholder + ').' 
          };
        }
        return { valid: true, country: fmt.name };
      }
    }

    // Unknown country code — just check reasonable length (7-15 digits per ITU E.164)
    if (digitsOnly.length >= 7 && digitsOnly.length <= 15) {
      return { valid: true };
    }
    
    return { valid: false, error: 'Phone number is not valid. Please enter a valid international number with country code.' };
  }

  // ========== EMAIL VALIDATION ==========
  function validateEmail(email) {
    if (!email) return { valid: false, error: 'Email address is required.' };
    
    email = email.trim().toLowerCase();
    
    // Basic format check
    var emailRegex = /^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(email)) {
      return { valid: false, error: 'Please enter a valid email address (e.g., you@example.com).' };
    }
    
    // Check for disposable domains
    var domain = email.split('@')[1];
    if (DISPOSABLE_DOMAINS.indexOf(domain) !== -1) {
      return { valid: false, error: 'Please use a real business or personal email. Disposable/temporary emails are not accepted.' };
    }
    
    // Check for obvious fake patterns
    if (/^(test|fake|asdf|qwer|aaaa|xxxx)@/i.test(email)) {
      return { valid: false, error: 'Please enter your real email address.' };
    }
    
    return { valid: true };
  }

  // ========== RATE LIMITING ==========
  var RATE_LIMIT_MAX = 3;
  var RATE_LIMIT_HOURS = 24;

  function getRateLimitKey(formId) {
    return 'agl_form_submissions_' + formId;
  }

  function getSubmissions(formId) {
    try {
      var raw = localStorage.getItem(getRateLimitKey(formId));
      if (!raw) return [];
      var data = JSON.parse(raw);
      var now = Date.now();
      var cutoff = now - (RATE_LIMIT_HOURS * 60 * 60 * 1000);
      // Filter out expired entries
      return data.filter(function(ts) { return ts > cutoff; });
    } catch (e) {
      return [];
    }
  }

  function recordSubmission(formId) {
    var submissions = getSubmissions(formId);
    submissions.push(Date.now());
    try {
      localStorage.setItem(getRateLimitKey(formId), JSON.stringify(submissions));
    } catch (e) {}
  }

  function checkRateLimit(formId) {
    var submissions = getSubmissions(formId);
    if (submissions.length >= RATE_LIMIT_MAX) {
      var oldest = Math.min.apply(null, submissions);
      var resetTime = new Date(oldest + (RATE_LIMIT_HOURS * 60 * 60 * 1000));
      var hoursLeft = Math.ceil((resetTime.getTime() - Date.now()) / (1000 * 60 * 60));
      return {
        allowed: false,
        error: 'You have reached the maximum of ' + RATE_LIMIT_MAX + ' submissions per day. Please try again in ' + hoursLeft + ' hour' + (hoursLeft !== 1 ? 's' : '') + '.'
      };
    }
    return { allowed: true, remaining: RATE_LIMIT_MAX - submissions.length };
  }

  // ========== ERROR DISPLAY ==========
  function showFieldError(input, message) {
    clearFieldError(input);
    input.style.borderColor = '#ff4444';
    input.style.boxShadow = '0 0 0 2px rgba(255, 68, 68, 0.15)';
    var errorDiv = document.createElement('div');
    errorDiv.className = 'field-validation-error';
    errorDiv.style.cssText = 'color:#ff4444;font-size:0.8rem;margin-top:4px;padding:4px 0;';
    errorDiv.textContent = message;
    input.parentNode.appendChild(errorDiv);
  }

  function clearFieldError(input) {
    input.style.borderColor = '';
    input.style.boxShadow = '';
    var existing = input.parentNode.querySelector('.field-validation-error');
    if (existing) existing.remove();
  }

  function showFormError(form, message) {
    clearFormError(form);
    var errorDiv = document.createElement('div');
    errorDiv.className = 'form-rate-limit-error';
    errorDiv.style.cssText = 'text-align:center;padding:16px;background:rgba(255,68,68,0.12);border:1px solid rgba(255,68,68,0.3);border-radius:8px;margin-bottom:16px;color:#ff6b6b;font-weight:500;font-size:0.9rem;';
    errorDiv.textContent = message;
    form.insertBefore(errorDiv, form.firstChild);
  }

  function clearFormError(form) {
    var existing = form.querySelector('.form-rate-limit-error');
    if (existing) existing.remove();
  }

  // ========== PUBLIC API ==========
  window.AGLFormValidation = {
    validatePhone: validatePhone,
    validateEmail: validateEmail,
    checkRateLimit: checkRateLimit,
    recordSubmission: recordSubmission,
    showFieldError: showFieldError,
    clearFieldError: clearFieldError,
    showFormError: showFormError,
    clearFormError: clearFormError,

    /**
     * Full form validation. Returns true if all valid, false if errors.
     * @param {Object} options - { formId, emailInput, phoneInput }
     */
    validateForm: function(options) {
      var hasError = false;
      var formId = options.formId;
      var form = document.getElementById(formId);

      // Rate limit check first
      if (form) clearFormError(form);
      var rateCheck = checkRateLimit(formId);
      if (!rateCheck.allowed) {
        if (form) showFormError(form, rateCheck.error);
        return false;
      }

      // Email validation
      if (options.emailInput) {
        var emailInput = options.emailInput;
        clearFieldError(emailInput);
        var emailResult = validateEmail(emailInput.value);
        if (!emailResult.valid) {
          showFieldError(emailInput, emailResult.error);
          hasError = true;
        }
      }

      // Phone validation
      if (options.phoneInput && options.phoneInput.value.trim()) {
        var phoneInput = options.phoneInput;
        clearFieldError(phoneInput);
        var phoneResult = validatePhone(phoneInput.value);
        if (!phoneResult.valid) {
          showFieldError(phoneInput, phoneResult.error);
          hasError = true;
        }
      }

      // If phone is required and empty
      if (options.phoneRequired && options.phoneInput && !options.phoneInput.value.trim()) {
        showFieldError(options.phoneInput, 'Phone number is required.');
        hasError = true;
      }

      return !hasError;
    }
  };
})();
