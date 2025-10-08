<?php
/**
 * Bulk Import Script - Uses Laravel directly
 */

require __DIR__ . '/../../vendor/autoload.php';

$app = require_once __DIR__ . '/../../bootstrap/app.php';
$kernel = $app->make(Illuminate\Contracts\Console\Kernel::class);
$kernel->bootstrap();

use Illuminate\Support\Facades\Log;

$uploadsDir = '/home/gagneet/home-expenses/uploads';

$bankMapping = [
    'AMEX-BusinessPlatinum-43006' => 'amex',
    'AMEX-CashBack-71006' => 'amex',
    'CBA-87Hoolihan-9331' => 'commbank_offset',
    'CBA-EveryDayOffset-7964' => 'commbank_offset',
    'CBA-HomeLoan-466297723' => 'commbank_homeloan',
    'CBA-HomeLoan-466297731' => 'commbank_homeloan',
    'CBA-HomeLoan-470379959' => 'commbank_homeloan',
    'CBA-MasterCard-6233' => 'commbank',
    'CBA-PL-466953719' => 'commbank_homeloan',
    'ING-Everyday-64015854' => 'ing_orange',
    'ING-Saver-45070850' => 'ing_savings',
    'ING-Saver-817278720' => 'ing_savings',
    'uBank-86400-Gagneet' => 'ubank',
];

// Authenticate as user 1
$user = \FireflyIII\Models\User::find(1);
if (!$user) {
    echo "ERROR: User not found\n";
    exit(1);
}

auth()->login($user);
echo "✓ Authenticated as {$user->email}\n\n";

// Get access token for API
$tokenResult = DB::table('oauth_access_tokens')
    ->where('user_id', 1)
    ->where('revoked', 0)
    ->orderBy('created_at', 'DESC')
    ->first();

if ($tokenResult) {
    $token = $tokenResult->id;
} else {
    // Create new token
    $token = $user->createToken('Bulk Import')->accessToken;
}

echo "Access Token: " . substr($token, 0, 20) . "...\n\n";

// Save token for Python script
file_put_contents('/home/gagneet/.firefly_token', $token);
echo "✓ Token saved to ~/.firefly_token\n\n";

echo "Now run: python3 /home/gagneet/firefly/data-importer/bulk_import_all.py\n";
