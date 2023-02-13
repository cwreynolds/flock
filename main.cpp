//File: main.cpp

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// TODO 20230212 comment these out to debug cmake build
//#include <GL/glew.h> // include GLEW and new version of GL on Windows
//#include <GLFW/glfw3.h> // GLFW helper library for window management
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#include <iostream> //for cout

////////////////////////////////////////////////////////////////////////////////
// TODO 20230206 draw something
#include <chrono>
#include <thread>
using namespace std::chrono_literals;
////////////////////////////////////////////////////////////////////////////////

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// TODO 20230212 comment these out to debug cmake build

//int main (int argc, char** argv)
//{
//    // start GL context and O/S window using the GLFW helper library
//    if (!glfwInit ())
//    {
//        std::cerr<<"ERROR: could not start GLFW3"<<std::endl;
//        return 1;
//    }
//
//    //Setting window properties
//    glfwWindowHint (GLFW_CONTEXT_VERSION_MAJOR, 3);
//    glfwWindowHint (GLFW_CONTEXT_VERSION_MINOR, 2);
//    glfwWindowHint (GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);
//    glfwWindowHint (GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
//
//    //Actually create the window
//    GLFWwindow* window = glfwCreateWindow (640, 480, "OpenGL Initialization Example", NULL, NULL);
//    if (!window)
//    {
//        std::cerr<<"ERROR: could not open window with GLFW3"<<std::endl;
//        glfwTerminate();
//        return 1;
//    }
//    glfwMakeContextCurrent (window);
//
//    // start GLEW extension handler
//    glewExperimental = GL_TRUE;
//    glewInit ();
//
//    ////////////////////////////////////////////////////////////////////////////
//    // TODO 20230206 draw something
//
////    glClearColor(0.2f, 0.3f, 0.3f, 1.0f);
//    glClearColor(1, 1, 1, 1);
//    glClear(GL_COLOR_BUFFER_BIT);
//
//
//    // glfw: swap buffers and poll IO events (keys pressed/released, mouse moved etc.)
//    // -------------------------------------------------------------------------------
//    glfwSwapBuffers(window);
//    glfwPollEvents();
//
//    std::this_thread::sleep_for(2000ms);
//
//    ////////////////////////////////////////////////////////////////////////////
//
//    // get version info
//    const GLubyte* renderer = glGetString (GL_RENDERER); // get renderer string
//    const GLubyte* version = glGetString (GL_VERSION); // version as a string
//    std::cout<<"Renderer: "<<renderer<<std::endl;
//    std::cout<<"OpenGL version supported "<<version<<std::endl;
//
//    // close GL context and any other GLFW resources
//    glfwTerminate();
//    return 0;
//}


int main (int argc, char** argv)
{
    std::cout << "Hello!" << std::endl;
    return 0;
}
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
