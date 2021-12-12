#include <cppcms/application.h>  
#include <cppcms/applications_pool.h>  
#include <cppcms/service.h>  
#include <cppcms/http_response.h>
#include <cppcms/cppcms_error.h>
#include <iostream> 

class hello : public cppcms::application {  
public:  
    hello(cppcms::service &srv) :  
        cppcms::application(srv)  
    {  
    }  
    virtual void main(std::string url)
    {
    }
}; 

int main(int argc, char ** argv)  
{  
    try {  
        cppcms::service srv(argc, argv); 
        srv.applications_pool().mount(cppcms::applications_factory<hello>());  
        //srv.run();  
    }  
    catch(const cppcms::cppcms_error& e) {  
        std::cerr << "Unable to start: " << e.what() << std::endl; 
        return 0;
    }
    catch (const std::exception& e)
    {
        std::cerr << "Unknown error: " << e.what() << std::endl;
        return 1;
    }
    return 0;
}  
