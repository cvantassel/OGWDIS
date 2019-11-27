import mysql.connector as conn


class dbClient():
    """https://dev.mysql.com/doc/connector-python/en/connector-python-reference.html"""

    def __init__(self, config:dict):

        self.og_conn = og_conn = conn.connect(**config)
        self.cursor = og_conn.cursor()
    
    def set_handle(self, handle):
        self.handle = handle

    def run_query(self, query):
        response = self.cursor.execute(query)
        result = []
        for row in self.cursor:
            result.append(row)
        return result


    def run_multi_query(self, queries: list):
    
        result = []
        try:
            responses = self.cursor.execute(query, multi=True)
            self.og_conn.commit()

            for response in responses:
                for record in response:
                    result.append(record)
            
            return str(result)
        except Exception as ex:
            return str(ex)

    def run_get_data_procedure(self, proc_name:str, arguments:list):
        
        result = []
        
        try:
            self.cursor.callproc(proc_name, [username])
            self.og_conn.commit()

            for response in self.cursor.stored_results():
                for record in response.fetchall():
                    result.append(str(record))
            
            return result
        
        except Exception as ex:
            print(ex)
    
    def get_follow_count(self)->int:
        query = "select followers from twitterAccount where handle = '%s';" % (self.handle)
        return self.run_query(query)[0][0]
        


    def close_connection(self):
        self.og_conn.close()
