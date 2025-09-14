"use client";

import React, { useState, useEffect } from 'react';
import BarcodeScanner from '../../../components/BarcodeScanner';

interface Product {
  id: string;
  name: string;
  sku: string;
  barcode?: string;
  sale_price?: number;
  stock_quantity: number;
}

interface StockMove {
  id: string;
  product_id: string;
  quantity: number;
  move_type: string;
  reference?: string;
  status: string;
  created_at: string;
}

interface BarcodeSearchResult {
  found: boolean;
  product?: Product;
  barcode: string;
}

const InventoryPage: React.FC = () => {
  const [scannerActive, setScannerActive] = useState(false);
  const [lastScannedBarcode, setLastScannedBarcode] = useState<string>('');
  const [searchResult, setSearchResult] = useState<BarcodeSearchResult | null>(null);
  const [stockMoves, setStockMoves] = useState<StockMove[]>([]);
  const [selectedMoveType, setSelectedMoveType] = useState<string>('purchase');
  const [quantity, setQuantity] = useState<number>(1);
  const [reference, setReference] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [notification, setNotification] = useState<{ type: 'success' | 'error' | 'info'; message: string } | null>(null);

  // Simulated API functions (would connect to actual backend)
  const searchByBarcode = async (barcode: string): Promise<BarcodeSearchResult> => {
    // Simulate API call
    return new Promise((resolve) => {
      setTimeout(() => {
        // Mock response - in real app this would call /api/v1/inventory/barcode/{barcode}
        const mockProducts: Product[] = [
          { id: '1', name: 'Sample Product A', sku: 'SKU001', barcode: '1234567890123', sale_price: 29.99, stock_quantity: 50 },
          { id: '2', name: 'Sample Product B', sku: 'SKU002', barcode: '9876543210987', sale_price: 15.50, stock_quantity: 25 }
        ];
        
        const found = mockProducts.find(p => p.barcode === barcode);
        resolve({
          found: !!found,
          product: found,
          barcode: barcode
        });
      }, 500);
    });
  };

  const createStockMove = async (moveData: {
    product_id: string;
    quantity: number;
    move_type: string;
    reference?: string;
  }) => {
    // Simulate API call to /api/v1/inventory/moves
    return new Promise((resolve) => {
      setTimeout(() => {
        const newMove: StockMove = {
          id: Date.now().toString(),
          ...moveData,
          status: 'confirmed',
          created_at: new Date().toISOString()
        };
        resolve(newMove);
      }, 300);
    });
  };

  const handleBarcodeScanned = async (barcode: string) => {
    setLastScannedBarcode(barcode);
    setIsLoading(true);
    
    try {
      const result = await searchByBarcode(barcode);
      setSearchResult(result);
      
      if (result.found) {
        showNotification('success', `Product found: ${result.product?.name}`);
      } else {
        showNotification('info', `No product found for barcode: ${barcode}`);
      }
    } catch (error) {
      showNotification('error', 'Failed to search for product');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateStockMove = async () => {
    if (!searchResult?.found || !searchResult.product) {
      showNotification('error', 'No product selected');
      return;
    }

    if (quantity <= 0) {
      showNotification('error', 'Quantity must be greater than 0');
      return;
    }

    setIsLoading(true);
    try {
      const moveData = {
        product_id: searchResult.product.id,
        quantity: selectedMoveType === 'sale' ? -quantity : quantity,
        move_type: selectedMoveType,
        reference: reference || undefined
      };

      const newMove = await createStockMove(moveData);
      setStockMoves(prev => [newMove as StockMove, ...prev]);
      showNotification('success', `Stock move created: ${quantity} units ${selectedMoveType}`);
      
      // Reset form
      setQuantity(1);
      setReference('');
      setSearchResult(null);
    } catch (error) {
      showNotification('error', 'Failed to create stock move');
    } finally {
      setIsLoading(false);
    }
  };

  const showNotification = (type: 'success' | 'error' | 'info', message: string) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 5000);
  };

  const moveTypes = [
    { value: 'purchase', label: 'Purchase (Stock In)', icon: '📦' },
    { value: 'sale', label: 'Sale (Stock Out)', icon: '🛒' },
    { value: 'transfer', label: 'Transfer', icon: '🔄' },
    { value: 'adjustment', label: 'Adjustment', icon: '⚖️' },
    { value: 'return', label: 'Return', icon: '↩️' },
    { value: 'damage', label: 'Damage/Loss', icon: '💥' }
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            📱 Inventory Management
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Scan barcodes and manage stock movements
          </p>
        </div>

        {/* Notification */}
        {notification && (
          <div className={`mb-6 p-4 rounded-lg border ${
            notification.type === 'success' ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800 text-green-700 dark:text-green-300' :
            notification.type === 'error' ? 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-700 dark:text-red-300' :
            'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-300'
          }`}>
            <div className="flex items-center space-x-2">
              <span>{notification.type === 'success' ? '✅' : notification.type === 'error' ? '❌' : 'ℹ️'}</span>
              <span>{notification.message}</span>
            </div>
          </div>
        )}

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left Column - Barcode Scanner */}
          <div className="space-y-6">
            {/* Scanner Controls */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  📷 Barcode Scanner
                </h2>
                <button
                  onClick={() => setScannerActive(!scannerActive)}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    scannerActive
                      ? 'bg-red-600 hover:bg-red-700 text-white'
                      : 'bg-blue-600 hover:bg-blue-700 text-white'
                  }`}
                >
                  {scannerActive ? 'Stop Scanner' : 'Start Scanner'}
                </button>
              </div>
              
              <BarcodeScanner
                isActive={scannerActive}
                onScan={handleBarcodeScanned}
                onError={(error) => showNotification('error', error)}
              />
            </div>

            {/* Product Search Result */}
            {searchResult && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                  🔍 Search Result
                </h2>
                
                {searchResult.found && searchResult.product ? (
                  <div className="space-y-4">
                    <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="font-semibold text-green-900 dark:text-green-100">
                            {searchResult.product.name}
                          </h3>
                          <p className="text-sm text-green-700 dark:text-green-300">
                            SKU: {searchResult.product.sku}
                          </p>
                          <p className="text-sm text-green-700 dark:text-green-300">
                            Barcode: {searchResult.product.barcode}
                          </p>
                          <p className="text-sm text-green-700 dark:text-green-300">
                            Stock: {searchResult.product.stock_quantity} units
                          </p>
                          {searchResult.product.sale_price && (
                            <p className="text-sm text-green-700 dark:text-green-300">
                              Price: ${searchResult.product.sale_price}
                            </p>
                          )}
                        </div>
                        <span className="text-2xl">✅</span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">❓</span>
                      <div>
                        <h3 className="font-semibold text-yellow-900 dark:text-yellow-100">
                          Product Not Found
                        </h3>
                        <p className="text-sm text-yellow-700 dark:text-yellow-300">
                          Barcode: {searchResult.barcode}
                        </p>
                        <button className="mt-2 text-sm text-yellow-800 dark:text-yellow-200 underline hover:no-underline">
                          Create New Product
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Right Column - Stock Move Form */}
          <div className="space-y-6">
            {/* Stock Move Form */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                📊 Create Stock Move
              </h2>

              <div className="space-y-4">
                {/* Move Type */}
                <div>
                  <label htmlFor="moveType" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Movement Type
                  </label>
                  <select
                    id="moveType"
                    value={selectedMoveType}
                    onChange={(e) => setSelectedMoveType(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
                  >
                    {moveTypes.map((type) => (
                      <option key={type.value} value={type.value}>
                        {type.icon} {type.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Quantity */}
                <div>
                  <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Quantity
                  </label>
                  <input
                    id="quantity"
                    type="number"
                    min="1"
                    value={quantity}
                    onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
                  />
                </div>

                {/* Reference */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Reference (Optional)
                  </label>
                  <input
                    type="text"
                    value={reference}
                    onChange={(e) => setReference(e.target.value)}
                    placeholder="PO#, SO#, or other reference"
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
                  />
                </div>

                {/* Submit Button */}
                <button
                  onClick={handleCreateStockMove}
                  disabled={!searchResult?.found || isLoading}
                  className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors"
                >
                  {isLoading ? '⏳ Processing...' : '✅ Create Stock Move'}
                </button>
              </div>
            </div>

            {/* Recent Stock Moves */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                📋 Recent Moves
              </h2>

              {stockMoves.length === 0 ? (
                <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                  No stock moves recorded yet
                </p>
              ) : (
                <div className="space-y-3">
                  {stockMoves.slice(0, 5).map((move) => (
                    <div key={move.id} className="p-3 border border-gray-200 dark:border-gray-600 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <span className="font-medium text-gray-900 dark:text-white">
                            {moveTypes.find(t => t.value === move.move_type)?.icon} {move.move_type}
                          </span>
                          <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">
                            {move.quantity > 0 ? '+' : ''}{move.quantity} units
                          </span>
                        </div>
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          {new Date(move.created_at).toLocaleTimeString()}
                        </span>
                      </div>
                      {move.reference && (
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          Ref: {move.reference}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InventoryPage;