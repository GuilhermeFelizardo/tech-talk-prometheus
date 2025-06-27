import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export let options = {
    stages: [
        { duration: '30s', target: 10 }, // Subir para 10 usuários em 30s
        { duration: '1m', target: 20 },  // Manter 20 usuários por 1 minuto
        { duration: '30s', target: 30 }, // Subir para 30 usuários em 30s
        { duration: '1m', target: 30 },  // Manter 30 usuários por 1 minuto
        { duration: '30s', target: 0 },  // Descer para 0 usuários em 30s
    ],
    thresholds: {
        http_req_duration: ['p(95)<1000'], // 95% das requisições devem ser < 1s
        http_req_failed: ['rate<0.1'],     // Taxa de erro < 10%
        errors: ['rate<0.1'],              // Taxa de erro customizada < 10%
    },
};

const BASE_URL = 'https://app-1.guilhermefreis.com';
//const BASE_URL = 'http://localhost:5000';

export default function () {
    const endpoints = [
        '/',
        '/dashboard',
        '/api/metrics-demo',
        '/health',
        '/metrics',
        '/simulate-load?type=normal',
    ];
    
    const randomEndpoint = endpoints[Math.floor(Math.random() * endpoints.length)];
    const url = `${BASE_URL}${randomEndpoint}`;
    
    const response = http.get(url, {
        timeout: '10s',
        tags: { endpoint: randomEndpoint },
    });
    
    const success = check(response, {
        'status is 200': (r) => r.status === 200,
        'response time < 2s': (r) => r.timings.duration < 2000,
        'body contains content': (r) => r.body.length > 0,
    });
    
    errorRate.add(!success);
    
    sleep(Math.random() * 2 + 1);
}

export function setup() {
    console.log(`URL: ${BASE_URL}`);
    
    const response = http.get(`${BASE_URL}/health`);
    if (response.status !== 200) {
        throw new Error(`Aplicação não está respondendo. Status: ${response.status}`);
    }
    
    console.log('App online');
}

export function teardown() {
    console.log('Teste de carga finalizado');
}