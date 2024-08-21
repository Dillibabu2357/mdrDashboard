''' MDR Dashboard Service
======================

This service provides API endpoints to retrieve and display dashboard data for various applications. It also provides an API documentation endpoint using Swagger.

Author: Your Name

Dependencies:
-------------
- Flask: A micro web framework for Python.
- Flask-RESTx: An extension for creating RESTful APIs with Swagger documentation.
- PyYAML: A YAML parser and emitter for Python.
- sqlDashboardCountsQuery: A custom module for querying SQL databases for dashboard counts.'''


from flask import Flask
from flask_restx import Api, Resource, fields
import yaml
import sqlDashboardCountsQuery

app = Flask(__name__)
api = Api(app, version='1.0', title='MDR Dashboard', description='MDR Dashboard API')

yamlFile = yaml.load(open("db_credentials.yaml"), yaml.SafeLoader)

dashboard_model = api.model('Dashboard', {
    'Manuscripts': fields.Integer(description='Count of Manuscripts'),
    'Books': fields.Integer(description='Count of Books'),
    'Articles': fields.Integer(description='Count of Articles'),
    'Users': fields.Integer(description='Count of Users')
})

allcounts_model = api.model('AllCounts', {
    'database_name': fields.Nested(dashboard_model, description='Counts of documents and users for a mdrDashboard database')
})




@api.route('/spec')
class SwaggerSpec(Resource):
    def get(self):
        """
        Swagger API Documentation Endpoint
        ----------------------------------
        Returns the Swagger API documentation for this service.

        Returns:
            JSON: Swagger documentation for the MDR Dashboard service.
        """
        return api.spec




@api.route('/')
class HelloWorld(Resource):
    def get(self):
        """
        Root Endpoint
        -------------
        A simple endpoint to test if the service is running. It returns a welcome message.

        Returns:
            dict: A welcome message.
        """
        return {'message': 'Hello from MDR Dashboard service!'}

    



@api.route('/app/<string:prefix>')
class Dashboard(Resource):
    @api.doc(params={'prefix': 'The prefix that identifies the application.'})
    @api.marshal_with(dashboard_model)
    def get(self, prefix):
        """
        Dashboard Data for a Specific App
        ---------------------------------
        Returns dashboard data for a specific application based on the provided prefix.

        Args:
            prefix (str): The prefix that identifies the application.

        Returns:
            JSON: The dashboard data for the specified application.
        """
        return sqlDashboardCountsQuery.getDataQryResults(yamlFile[prefix]['db'])





@api.route('/allcounts')
class AllCounts(Resource):
    @api.marshal_with(allcounts_model)
    def get(self):
        """
        Aggregated Dashboard Data
        -------------------------
        Returns aggregated dashboard data from all databases.

        Returns:
            JSON: Aggregated dashboard data across all databases.
        """
        return sqlDashboardCountsQuery.getDataQryResultsAll()





if __name__ == "__main__":
    from werkzeug.serving import run_simple
    run_simple("127.0.0.1", 5000, app)

