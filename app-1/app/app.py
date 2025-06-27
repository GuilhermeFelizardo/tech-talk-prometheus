import random
import time
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Histogram, Gauge, Summary, generate_latest, CONTENT_TYPE_LATEST
import threading
import psutil

# Inicializa a aplicação Flask
app = Flask(__name__)

# Métricas customizadas do Prometheus
REQUEST_COUNT = Counter('darede_requests_total', 'Total de requisições', ['endpoint', 'method'])
REQUEST_DURATION = Histogram('darede_request_duration_seconds', 'Duração das requisições')
ACTIVE_USERS = Gauge('darede_active_users', 'Usuários ativos no momento')
MEMORY_USAGE = Gauge('darede_memory_usage_bytes', 'Uso de memória da aplicação')
BUSINESS_METRICS = Counter('darede_business_events_total', 'Eventos de negócio', ['event_type'])

# Configurações do Prometheus
def configure_prometheus(app):
    metrics = PrometheusMetrics(app)
    metrics.info('app_info', 'Application info', version='1.0', service='app-1')
    def update_system_metrics():
        while True:
            try:
                # Simula usuários ativos (para demonstração)
                ACTIVE_USERS.set(random.randint(10, 50))
                
                # Métricas reais de memória
                memory_info = psutil.Process().memory_info()
                MEMORY_USAGE.set(memory_info.rss)
                
                time.sleep(5)
            except:
                pass
    
    metrics_thread = threading.Thread(target=update_system_metrics, daemon=True)
    metrics_thread.start()
    
    return metrics

def setup_routes(app):
    
    @app.route("/")
    def home():
        REQUEST_COUNT.labels(endpoint='home', method='GET').inc()
        with REQUEST_DURATION.time():
            random_sleep(0.1, 0.5)  # Menos delay para melhor UX
            return render_template('index.html')

    @app.route("/dashboard")
    def dashboard():
        REQUEST_COUNT.labels(endpoint='dashboard', method='GET').inc()
        with REQUEST_DURATION.time():
            random_sleep(0.1, 0.3)
            return render_template('dashboard.html')

    @app.route("/api/metrics-demo")
    def metrics_demo():
        REQUEST_COUNT.labels(endpoint='api_metrics', method='GET').inc()
        with REQUEST_DURATION.time():

            event_types = ['login', 'purchase', 'view_product', 'search']
            event = random.choice(event_types)
            BUSINESS_METRICS.labels(event_type=event).inc()
            
            data = {
                'timestamp': datetime.now().isoformat(),
                'event_generated': event,
                'active_users': random.randint(15, 45),
                'response_time': round(random.uniform(0.1, 2.0), 3),
                'memory_mb': round(psutil.Process().memory_info().rss / 1024 / 1024, 2)
            }
            
            random_sleep(0.05, 0.2)
            return jsonify(data)

    @app.route("/simulate-load")
    def simulate_load():
        REQUEST_COUNT.labels(endpoint='simulate_load', method='GET').inc()
        with REQUEST_DURATION.time():

            load_type = request.args.get('type', 'normal')
            
            if load_type == 'high':

                random_sleep(2, 5)
                for _ in range(5):
                    BUSINESS_METRICS.labels(event_type='high_load_event').inc()
            elif load_type == 'error':

                if random.random() < 0.5:
                    BUSINESS_METRICS.labels(event_type='error').inc()
                    return jsonify({'error': 'Erro simulado para demonstração'}), 500
            
            random_sleep(0.1, 0.5)
            return jsonify({'status': 'load_simulated', 'type': load_type})

    @app.route("/health")
    def health():
        REQUEST_COUNT.labels(endpoint='health', method='GET').inc()
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'Darede Prometheus Demo'
        })

    @app.route("/metrics")
    def metrics():
        """Endpoint para métricas do Prometheus"""
        return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}


def random_sleep(min_time=0.1, max_time=1.0):
    time.sleep(random.uniform(min_time, max_time))

if __name__ == '__main__':
    configure_prometheus(app)
    setup_routes(app)
    app.run(host='0.0.0.0', port=5000, debug=True)