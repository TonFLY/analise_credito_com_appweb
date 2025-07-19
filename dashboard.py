import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import datetime, timedelta
from config import Config
import logging

st.set_page_config(
    page_title="Dashboard - Análise de Crédito",
    page_icon="📊",
    layout="wide"
)

def load_predictions_data():
    """Carrega dados de predições do log"""
    try:
        predictions = []
        log_file = f'{Config.LOGS_DIR}/predictions.log'
        
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        predictions.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue
        
        return pd.DataFrame(predictions)
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

def main():
    st.title("📊 Dashboard de Análise de Crédito")
    st.sidebar.title("Navegação")
    
    # Carrega dados
    df = load_predictions_data()
    
    if df.empty:
        st.warning("📊 Nenhum dado de predição encontrado. Execute algumas análises primeiro!")
        st.info("💡 Vá para a aplicação principal e faça algumas consultas de crédito.")
        return
    
    # Converte timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    df['hour'] = df['timestamp'].dt.hour
    
    # Sidebar com filtros
    st.sidebar.subheader("🔍 Filtros")
    
    # Filtro de data
    if len(df) > 0:
        min_date = df['date'].min()
        max_date = df['date'].max()
        
        date_range = st.sidebar.date_input(
            "Período",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            df_filtered = df[
                (df['date'] >= date_range[0]) & 
                (df['date'] <= date_range[1])
            ]
        else:
            df_filtered = df
    else:
        df_filtered = df
    
    # Métricas principais
    st.header("📈 Métricas Gerais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total de Predições",
            len(df_filtered),
            delta=len(df_filtered) - len(df) + len(df_filtered) if len(df) > len(df_filtered) else None
        )
    
    with col2:
        if len(df_filtered) > 0:
            avg_prob = df_filtered['probability'].mean()
            st.metric(
                "Probabilidade Média",
                f"{avg_prob:.2%}",
                delta=f"{avg_prob - 0.5:.2%}" if avg_prob != 0.5 else None
            )
    
    with col3:
        if len(df_filtered) > 0:
            good_clients = (df_filtered['probability'] > 0.5).sum()
            st.metric(
                "Clientes 'Bons'",
                good_clients,
                delta=f"{good_clients/len(df_filtered):.1%}"
            )
    
    with col4:
        if len(df_filtered) > 0:
            avg_time = df_filtered['processing_time_ms'].mean()
            st.metric(
                "Tempo Médio (ms)",
                f"{avg_time:.1f}ms",
                delta="⚡ Rápido" if avg_time < 1000 else "⏳ Lento"
            )
    
    # Gráficos
    if len(df_filtered) > 0:
        st.header("📊 Análises Visuais")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Distribuição de Probabilidades")
            fig_hist = px.histogram(
                df_filtered, 
                x='probability',
                bins=20,
                title="Distribuição das Probabilidades de Bom Pagador",
                color_discrete_sequence=['#1f77b4']
            )
            fig_hist.update_layout(
                xaxis_title="Probabilidade",
                yaxis_title="Frequência"
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            st.subheader("Predições por Hora")
            hourly_counts = df_filtered.groupby('hour').size().reset_index(name='count')
            fig_hourly = px.bar(
                hourly_counts,
                x='hour',
                y='count',
                title="Volume de Consultas por Hora",
                color_discrete_sequence=['#ff7f0e']
            )
            fig_hourly.update_layout(
                xaxis_title="Hora do Dia",
                yaxis_title="Número de Consultas"
            )
            st.plotly_chart(fig_hourly, use_container_width=True)
        
        # Gráfico de linha temporal
        st.subheader("Tendência Temporal")
        daily_stats = df_filtered.groupby('date').agg({
            'probability': 'mean',
            'processing_time_ms': 'mean'
        }).reset_index()
        
        fig_timeline = go.Figure()
        
        fig_timeline.add_trace(go.Scatter(
            x=daily_stats['date'],
            y=daily_stats['probability'],
            mode='lines+markers',
            name='Probabilidade Média',
            line=dict(color='#2ca02c', width=3)
        ))
        
        fig_timeline.update_layout(
            title="Evolução da Probabilidade Média ao Longo do Tempo",
            xaxis_title="Data",
            yaxis_title="Probabilidade Média",
            yaxis=dict(range=[0, 1])
        )
        
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Análise de Performance
        st.subheader("⚡ Performance do Sistema")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_perf = px.line(
                df_filtered.tail(100),  # Últimas 100 predições
                y='processing_time_ms',
                title="Tempo de Processamento (Últimas 100 Predições)",
                color_discrete_sequence=['#d62728']
            )
            fig_perf.update_layout(
                xaxis_title="Predições",
                yaxis_title="Tempo (ms)"
            )
            st.plotly_chart(fig_perf, use_container_width=True)
        
        with col2:
            # Box plot de tempos por resultado
            df_filtered['resultado'] = df_filtered['probability'].apply(
                lambda x: 'Bom' if x > 0.5 else 'Ruim'
            )
            
            fig_box = px.box(
                df_filtered,
                x='resultado',
                y='processing_time_ms',
                title="Tempo de Processamento por Resultado",
                color='resultado'
            )
            st.plotly_chart(fig_box, use_container_width=True)
        
        # Tabela de dados recentes
        st.subheader("📋 Predições Recentes")
        recent_data = df_filtered.tail(10)[['timestamp', 'probability', 'processing_time_ms']].copy()
        recent_data['probability'] = recent_data['probability'].apply(lambda x: f"{x:.2%}")
        recent_data['processing_time_ms'] = recent_data['processing_time_ms'].apply(lambda x: f"{x:.1f}ms")
        recent_data = recent_data.rename(columns={
            'timestamp': 'Data/Hora',
            'probability': 'Probabilidade',
            'processing_time_ms': 'Tempo (ms)'
        })
        
        st.dataframe(recent_data, use_container_width=True)

if __name__ == "__main__":
    main()
