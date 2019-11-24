import mysql.connector as conn


class dbClient():
    """https://dev.mysql.com/doc/connector-python/en/connector-python-reference.html"""

    def __init__(self, config:dict):

        self.og_conn = og_conn = conn.connect(**config)
        self.cursor = og_conn.cursor()

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

    def close_connection(self):
        self.og_conn.close()
