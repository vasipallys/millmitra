import { useState, useCallback } from 'react';

export const useBiometric = () => {
  const [isSupported, setIsSupported] = useState(false);
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [error, setError] = useState(null);

  // Check if biometric authentication is supported
  const checkSupport = useCallback(async () => {
    try {
      if (window.PublicKeyCredential && 
          typeof window.PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable === 'function') {
        const available = await window.PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
        setIsSupported(available);
        return available;
      }
      setIsSupported(false);
      return false;
    } catch (err) {
      console.error('Error checking biometric support:', err);
      setIsSupported(false);
      return false;
    }
  }, []);

  // Authenticate using biometrics
  const authenticate = useCallback(async () => {
    if (!isSupported) {
      throw new Error('Biometric authentication not supported');
    }

    setIsAuthenticating(true);
    setError(null);

    try {
      // Mock biometric authentication for demo
      // In a real implementation, this would use WebAuthn API
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Simulate success/failure
      const success = Math.random() > 0.2; // 80% success rate
      
      if (success) {
        setIsAuthenticating(false);
        return {
          success: true,
          biometricData: {
            type: 'fingerprint',
            timestamp: new Date().toISOString(),
            confidence: 0.95
          }
        };
      } else {
        throw new Error('Biometric authentication failed');
      }
    } catch (err) {
      setError(err.message);
      setIsAuthenticating(false);
      throw err;
    }
  }, [isSupported]);

  // Register biometric credentials
  const register = useCallback(async (userId) => {
    if (!isSupported) {
      throw new Error('Biometric registration not supported');
    }

    setIsAuthenticating(true);
    setError(null);

    try {
      // Mock biometric registration
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      setIsAuthenticating(false);
      return {
        success: true,
        credentialId: `cred_${userId}_${Date.now()}`,
        publicKey: 'mock_public_key_data'
      };
    } catch (err) {
      setError(err.message);
      setIsAuthenticating(false);
      throw err;
    }
  }, [isSupported]);

  return {
    isSupported,
    isAuthenticating,
    error,
    checkSupport,
    authenticate,
    register
  };
};
