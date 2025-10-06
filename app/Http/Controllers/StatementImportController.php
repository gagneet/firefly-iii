<?php

declare(strict_types=1);

namespace FireflyIII\Http\Controllers;

use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Storage;
use Symfony\Component\Process\Exception\ProcessFailedException;
use Symfony\Component\Process\Process;

/**
 * Class StatementImportController
 *
 * Handles Australian bank statement PDF uploads and imports
 */
class StatementImportController extends Controller
{
    /**
     * Show the statement import page
     */
    public function index()
    {
        return view('import.statement', [
            'VUE_SCRIPT_NAME' => 'app'
        ]);
    }

    /**
     * Get supported banks list
     */
    public function getSupportedBanks(): JsonResponse
    {
        $banks = [
            [
                'value' => 'amex',
                'label' => 'American Express (AMEX)',
                'description' => 'American Express credit card statements'
            ],
            [
                'value' => 'ing_orange',
                'label' => 'ING Orange Everyday',
                'description' => 'ING Orange Everyday transaction account'
            ],
            [
                'value' => 'ing_savings',
                'label' => 'ING Savings Maximiser',
                'description' => 'ING Savings Maximiser savings account'
            ],
            [
                'value' => 'ubank',
                'label' => 'uBank Spend',
                'description' => 'uBank Spend transaction account'
            ],
            [
                'value' => 'commbank',
                'label' => 'Commonwealth Bank',
                'description' => 'Commonwealth Bank accounts'
            ]
        ];

        return response()->json(['data' => $banks]);
    }

    /**
     * Upload and process PDF statement
     */
    public function upload(Request $request): JsonResponse
    {
        $request->validate([
            'file' => 'required|file|mimes:pdf|max:10240', // Max 10MB
            'bank_type' => 'required|string|in:amex,ing_orange,ing_savings,ubank,commbank',
            'detect_duplicates' => 'boolean',
            'detect_transfers' => 'boolean'
        ]);

        try {
            // Store uploaded file
            $file = $request->file('file');
            $filename = time() . '_' . $file->getClientOriginalName();
            $path = $file->storeAs('temp_statements', $filename);
            $fullPath = storage_path('app/' . $path);

            Log::info('Statement uploaded', [
                'filename' => $filename,
                'bank_type' => $request->input('bank_type'),
                'size' => $file->getSize()
            ]);

            // Process PDF and import transactions
            $result = $this->processStatement(
                $fullPath,
                $request->input('bank_type'),
                $request->input('detect_duplicates', true),
                $request->input('detect_transfers', true)
            );

            // Clean up uploaded file
            Storage::delete($path);

            if (isset($result['error'])) {
                return response()->json([
                    'success' => false,
                    'message' => $result['error']
                ], 422);
            }

            return response()->json([
                'success' => true,
                'message' => 'Statement imported successfully',
                'data' => $result
            ]);

        } catch (\Exception $e) {
            Log::error('Statement import error', [
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);

            return response()->json([
                'success' => false,
                'message' => 'Error importing statement: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Process statement PDF using Python service
     */
    private function processStatement(
        string $pdfPath,
        string $bankType,
        bool $detectDuplicates,
        bool $detectTransfers
    ): array {
        $pythonScript = base_path('../data-importer/firefly_service.py');
        $fireflyUrl = config('app.url');
        $accessToken = $this->getUserAccessToken();

        if (!$accessToken) {
            return ['error' => 'No access token available. Please configure your Personal Access Token.'];
        }

        // Build Python command
        $command = [
            'python3',
            $pythonScript,
            $bankType,
            $pdfPath,
            $fireflyUrl,
            $accessToken
        ];

        $process = new Process($command);
        $process->setTimeout(60); // 60 seconds timeout

        try {
            $process->mustRun();

            $output = $process->getOutput();
            Log::info('Python process output', ['output' => $output]);

            // Parse output for results
            // The Python script outputs JSON-like results
            if (preg_match('/total\s*:\s*(\d+)/i', $output, $matches)) {
                $total = (int)$matches[1];
            } else {
                $total = 0;
            }

            if (preg_match('/created\s*:\s*(\d+)/i', $output, $matches)) {
                $created = (int)$matches[1];
            } else {
                $created = 0;
            }

            if (preg_match('/duplicates\s*:\s*(\d+)/i', $output, $matches)) {
                $duplicates = (int)$matches[1];
            } else {
                $duplicates = 0;
            }

            if (preg_match('/transfers\s*:\s*(\d+)/i', $output, $matches)) {
                $transfers = (int)$matches[1];
            } else {
                $transfers = 0;
            }

            if (preg_match('/errors\s*:\s*(\d+)/i', $output, $matches)) {
                $errors = (int)$matches[1];
            } else {
                $errors = 0;
            }

            return [
                'total' => $total,
                'created' => $created,
                'duplicates' => $duplicates,
                'transfers' => $transfers,
                'errors' => $errors
            ];

        } catch (ProcessFailedException $exception) {
            Log::error('Python process failed', [
                'error' => $exception->getMessage(),
                'output' => $process->getOutput(),
                'error_output' => $process->getErrorOutput()
            ]);

            return ['error' => 'Failed to process statement: ' . $process->getErrorOutput()];
        }
    }

    /**
     * Get user's access token from session or generate one
     */
    private function getUserAccessToken(): ?string
    {
        // Try to get token from environment (for testing)
        $token = config('firefly.import_access_token');

        if ($token) {
            return $token;
        }

        // In production, you'd want to use the authenticated user's token
        // For now, we'll use a Passport token if available
        $user = auth()->user();

        if (!$user) {
            return null;
        }

        // Check if user has a personal access token
        $token = $user->tokens()->where('name', 'Statement Import')->first();

        if ($token) {
            return $token->accessToken;
        }

        // Create a new personal access token
        $newToken = $user->createToken('Statement Import');
        return $newToken->accessToken;
    }

    /**
     * Get import history
     */
    public function history(): JsonResponse
    {
        // This would query import logs from the database
        // For now, return empty array
        return response()->json(['data' => []]);
    }
}
