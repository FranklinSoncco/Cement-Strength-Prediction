import streamlit as st
from datetime import datetime
import logging
import pickle
import os


if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.logs'),
        logging.StreamHandler()  # También en consola
    ]
)

logger = logging.getLogger()

logger.info("App started")


st.title("Concrete Strength Predictor")

# Cargar modelo (cachear para performance)
@st.cache_resource
def load_model():
    try:
        model = pickle.load('linear_regression.pkl')
        logging.info("Model loaded successfully")
        return model
    except Exception as e:
        logging.error(f"Error loading model: {str(e)}")
        raise e

# Inicializar variables
model = None

try:
    model = load_model()
    if model is not None:
        st.success("✅ Modelo cargado correctamente")
    else:
        st.error("❌ Modelo no pudo ser cargado")
        st.stop()
except Exception as e:
    st.error(f"❌ Error cargando modelo: {str(e)}")
    st.stop()



st.sidebar.header("Características do Concreto")
cement = st.sidebar.number_input("Cimento (kg/m³)", min_value=0.0, value=300.0)
blast_furnace_slag = st.sidebar.number_input("Escória de Alto-Forno (kg/m³)", min_value=0.0, value=100.0)
fly_ash = st.sidebar.number_input("Cinza Volante (kg/m³)", min_value=0.0, value=50.0)
water = st.sidebar.number_input("Água (kg/m³)", min_value=0.0, value=180.0)
superplasticizer = st.sidebar.number_input("Superplastificante (kg/m³)", min_value=0.0, value=5.0)
coarse_aggregate = st.sidebar.number_input("Agregado Graúdo (kg/m³)", min_value=0.0, value=1000.0)
fine_aggregate = st.sidebar.number_input("Agregado Miúdo (kg/m³)", min_value=0.0, value=800.0)
age = st.sidebar.number_input("Idade (dias)", min_value=1, value=28)


if st.button("Calcular fuerza", type="primary", use_container_width=True):
    if cement < 0 or blast_furnace_slag < 0 or fly_ash < 0 or water < 0 or superplasticizer < 0 or coarse_aggregate < 0 or fine_aggregate < 0 or age <= 0:
        st.error("Por favor, ingrese valores válidos para todas las características.")
        logger.warning("Invalid input values provided")
    if cement is None or blast_furnace_slag is None or fly_ash is None or water is None or superplasticizer is None or coarse_aggregate is None or fine_aggregate is None or age is None:
        st.error("Por favor, ingrese valores para todas las características.")
        logger.warning("Missing input values provided")
    if model:
        start_time = datetime.now()
        input_data = [[cement, blast_furnace_slag, fly_ash, water, superplasticizer, coarse_aggregate, fine_aggregate, age]]
        prediction = model.predict(input_data)
        end_time = datetime.now()
        logger.info(f"Prediction made: {prediction[0]:.2f} MPa in {(end_time - start_time).total_seconds()} seconds")
        st.subheader(f"Predicción de la resistencia del concreto: {prediction[0]:.2f} MPa")
    else:
        st.error("El modelo no está disponible.")
        
st.markdown("---")
st.sidebar.subheader("Estadísticas de la Aplicación")
def get_app_stats():
    try:
        with open('logs/app.logs', 'rb') as f:
            logs = f.readlines()
        today = datetime.now().date()
        latencys = [l for l in logs if "Prediction made" in l.decode('utf-8')]
        avg_latency = sum([(datetime.strptime(l.decode('utf-8').split(" - ")[0], '%Y-%m-%d %H:%M:%S,%f') - datetime.strptime(l.decode('utf-8').split(" - ")[0], '%Y-%m-%d %H:%M:%S,%f')).total_seconds() for l in latencys]) / len(latencys) if latencys else 0
        return {"total_predictions": len(latencys), "average_latency": avg_latency}
    except Exception as e:
        logging.error(f"Error loading app stats: {str(e)}")
        return {"total_predictions": 0, "average_latency": 0.0}
    
app_stats = get_app_stats()
st.sidebar.write(f"Total de predicciones: {app_stats['total_predictions']}")
st.sidebar.write(f"Tiempo promedio de predicción: {app_stats['average_latency']:.2f} segundos")

