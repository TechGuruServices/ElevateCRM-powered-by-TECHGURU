"use client";

import React, { useState, useRef, useEffect } from 'react';
import { Html5QrcodeScanner, Html5Qrcode, Html5QrcodeScanType } from 'html5-qrcode';

interface BarcodeScannerProps {
  onScan: (decodedText: string) => void;
  onError?: (error: string) => void;
  isActive: boolean;
}

const BarcodeScanner: React.FC<BarcodeScannerProps> = ({
  onScan,
  onError,
  isActive
}) => {
  const [scannerState, setScannerState] = useState<'idle' | 'starting' | 'active' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const scannerRef = useRef<Html5QrcodeScanner | null>(null);
  const scannerElementId = "qr-reader";

  useEffect(() => {
    if (isActive && scannerState === 'idle') {
      startScanner();
    } else if (!isActive && scannerRef.current) {
      stopScanner();
    }

    return () => {
      if (scannerRef.current) {
        stopScanner();
      }
    };
  }, [isActive]);

  const startScanner = async () => {
    try {
      setScannerState('starting');
      setErrorMessage('');

      // Check if browser supports barcode scanning
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Camera access not supported in this browser');
      }

      // Try Html5QrcodeScanner first (more comprehensive)
      const scanner = new Html5QrcodeScanner(
        scannerElementId,
        {
          fps: 10,
          qrbox: { width: 300, height: 200 },
          aspectRatio: 1.777778, // 16:9
          rememberLastUsedCamera: true,
          supportedScanTypes: [
            // Support QR codes and camera scanning
            Html5QrcodeScanType.SCAN_TYPE_CAMERA
          ]
        },
        false // verbose
      );

      scannerRef.current = scanner;

      scanner.render(
        (decodedText: string) => {
          console.log('Barcode scanned:', decodedText);
          onScan(decodedText);
          setScannerState('active');
        },
        (error: any) => {
          // Only log actual errors, not "no QR code found" messages
          if (!error.toString().includes('NotFoundException')) {
            console.warn('Scanner error:', error);
          }
        }
      );

      setScannerState('active');
    } catch (error: any) {
      console.error('Failed to start scanner:', error);
      setErrorMessage(error.message || 'Failed to start camera');
      setScannerState('error');
      onError?.(error.message || 'Failed to start camera');
    }
  };

  const stopScanner = () => {
    if (scannerRef.current) {
      try {
        scannerRef.current.clear();
      } catch (error) {
        console.warn('Error stopping scanner:', error);
      }
      scannerRef.current = null;
    }
    setScannerState('idle');
  };

  const handleManualInput = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      const target = event.target as HTMLInputElement;
      if (target.value.trim()) {
        onScan(target.value.trim());
        target.value = '';
      }
    }
  };

  return (
    <div className="barcode-scanner w-full">
      {/* Scanner Status */}
      <div className="mb-4">
        <div className="flex items-center space-x-2">
          <div
            className={`w-3 h-3 rounded-full ${
              scannerState === 'active'
                ? 'bg-green-500'
                : scannerState === 'starting'
                ? 'bg-yellow-500'
                : scannerState === 'error'
                ? 'bg-red-500'
                : 'bg-gray-400'
            }`}
          />
          <span className="text-sm text-gray-600 dark:text-gray-300">
            {scannerState === 'active' && 'Scanner Active - Point camera at barcode'}
            {scannerState === 'starting' && 'Starting camera...'}
            {scannerState === 'error' && 'Scanner Error'}
            {scannerState === 'idle' && 'Scanner Inactive'}
          </span>
        </div>
      </div>

      {/* Error Message */}
      {errorMessage && (
        <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <div className="flex items-center space-x-2">
            <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-sm text-red-700 dark:text-red-300">{errorMessage}</span>
          </div>
        </div>
      )}

      {/* Scanner Element */}
      <div className="mb-4">
        <div
          id={scannerElementId}
          className={`${isActive ? 'block' : 'hidden'} border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg overflow-hidden`}
          style={{ minHeight: '250px' }}
        />
        
        {!isActive && (
          <div className="flex items-center justify-center h-64 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
            <div className="text-center">
              <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <p className="text-gray-500 dark:text-gray-400">Camera scanner inactive</p>
              <p className="text-sm text-gray-400 dark:text-gray-500">Enable scanning to use camera</p>
            </div>
          </div>
        )}
      </div>

      {/* Manual Input Fallback */}
      <div className="mb-4">
        <label htmlFor="manual-barcode" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Manual Barcode Entry
        </label>
        <input
          type="text"
          id="manual-barcode"
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
          placeholder="Type or scan barcode here, press Enter"
          onKeyDown={handleManualInput}
        />
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
          Supports UPC, EAN, Code 128, Code 39, and QR codes
        </p>
      </div>

      {/* Scanner Instructions */}
      <div className="text-sm text-gray-600 dark:text-gray-300">
        <h4 className="font-medium mb-2">Scanning Tips:</h4>
        <ul className="space-y-1 text-xs">
          <li>• Hold device steady and ensure good lighting</li>
          <li>• Position barcode within the scanning frame</li>
          <li>• Try different distances if scan doesn't work</li>
          <li>• Use manual entry if camera scanning fails</li>
        </ul>
      </div>
    </div>
  );
};

export default BarcodeScanner;