FROM python:3.12-slim AS wheels

WORKDIR /build
COPY backend/requirements.txt ./requirements.txt
RUN python -m pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    KENKOMIRAI_MOBILITY_CSV=/app/data/la_mobilityreports.csv \
    KENKOMIRAI_POPULATION_SHAPEFILE=/app/data/population/2020_Population_and_Poverty_at_Split_Tract.shp

RUN groupadd --system --gid 10001 kenko \
    && useradd --system --uid 10001 --gid kenko --home-dir /app kenko

WORKDIR /app
COPY --from=wheels /wheels /wheels
RUN python -m pip install --no-cache-dir /wheels/* && rm -rf /wheels
COPY --chown=kenko:kenko backend/app ./app
COPY --chown=kenko:kenko "initial datasets/la_mobilityreports.csv" ./data/la_mobilityreports.csv
COPY --chown=kenko:kenko "initial datasets/2020_Population/2020_Population_and_Poverty_at_Split_Tract.shp" ./data/population/2020_Population_and_Poverty_at_Split_Tract.shp
COPY --chown=kenko:kenko "initial datasets/2020_Population/2020_Population_and_Poverty_at_Split_Tract.shx" ./data/population/2020_Population_and_Poverty_at_Split_Tract.shx
COPY --chown=kenko:kenko "initial datasets/2020_Population/2020_Population_and_Poverty_at_Split_Tract.dbf" ./data/population/2020_Population_and_Poverty_at_Split_Tract.dbf
COPY --chown=kenko:kenko "initial datasets/2020_Population/2020_Population_and_Poverty_at_Split_Tract.prj" ./data/population/2020_Population_and_Poverty_at_Split_Tract.prj

USER kenko
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health', timeout=3)" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--proxy-headers"]
