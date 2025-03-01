FROM postgres:15

# Configure PostgreSQL to accept connections with no password 
RUN echo "host all all all trust" >> /var/lib/postgresql/data/pg_hba.conf

# Set up the database
ENV POSTGRES_DB=sqheaven_db
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=""

# Expose PostgreSQL port (internally only)
EXPOSE 5432

# Start PostgreSQL automatically
CMD ["postgres"]
