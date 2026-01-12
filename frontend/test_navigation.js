// Test script to verify navigation
console.log('Testing navigation setup...');

// Check if the route exists
const fs = require('fs');
const path = require('path');

const settingsGarminPath = path.join(__dirname, 'app/settings/garmin/page.tsx');
const dashboardPath = path.join(__dirname, 'app/dashboard/page.tsx');

console.log('Settings Garmin route exists:', fs.existsSync(settingsGarminPath));
console.log('Dashboard route exists:', fs.existsSync(dashboardPath));

// Check router import
const dashboardContent = fs.readFileSync(dashboardPath, 'utf8');
const hasRouterImport = dashboardContent.includes("import { useRouter }");
const hasRouterUsage = dashboardContent.includes("router.push('/settings/garmin')");

console.log('Dashboard has router import:', hasRouterImport);
console.log('Dashboard has navigation code:', hasRouterUsage);
