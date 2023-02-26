//------------------------------------------------------------------------------
//
// Draw.h -- new flock experiments
//
// Graphics utilities based on OpenGL
//
// MIT License -- Copyright © 2023 Craig Reynolds
//
//------------------------------------------------------------------------------

#pragma once

#include <GL/glew.h>    // Cross platform "OpenGL Extention Wrangle"
#include <GLFW/glfw3.h> // Cross platform library for window management
#include <iostream>     // c++ stream I/O

#include "Vec3.h"       // Cartesian 3d vector space utility.
#include "Boid.h"       // Boid class, specialization of Agent.

class Draw
{
public:
    // Constructors
    Draw() { init(); }
    Draw(int window_width, int window_height)
      : window_width_(window_width), window_height_(window_height) { init(); }
      
    void init()
    {
        sample_opengl_code();
        
        
        LocalSpace ls;
        std::cout << ls << std::endl;
    }

    // code from https://learnopengl.com/Getting-started/Hello-Triangle
    const char *vertexShaderSource =
        "#version 330 core                                    \
         layout (location = 0) in vec3 aPos;                  \
         void main()                                          \
         {                                                    \
             gl_Position = vec4(aPos.x, aPos.y, aPos.z, 1.0); \
         }";

    const char *fragmentShaderSource =
        "#version 330 core                             \
         out vec4 FragColor;                           \
         void main()                                   \
         {                                             \
             FragColor = vec4(1.0f, 0.5f, 0.2f, 1.0f); \
         }";

    int sample_opengl_code()
    {
        // start GL context and O/S window using the GLFW helper library
        if (!glfwInit ())
        {
            std::cerr<<"ERROR: could not start GLFW3"<<std::endl;
            return 1;
        }
        
        // glfw: initialize and configure
        glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
        glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
        glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
#ifdef __APPLE__
        glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);
#endif
        
        // glfw window creation
        GLFWwindow* window = glfwCreateWindow(window_width_, window_height_,
                                              "flock", NULL, NULL);
        if (window == NULL)
        {
            std::cout << "Failed to create GLFW window" << std::endl;
            glfwTerminate();
            return -1;
        }
        glfwMakeContextCurrent(window);
        glfwSetFramebufferSizeCallback(window, framebuffer_size_callback);
        
        // get version info
        const GLubyte* renderer = glGetString (GL_RENDERER); // get renderer string
        const GLubyte* version = glGetString (GL_VERSION); // version as a string
        std::cout<<"Renderer: "<<renderer<<std::endl;
        std::cout<<"OpenGL version supported "<<version<<std::endl;
        
        // start GLEW extension handler
        glewExperimental = GL_TRUE;
        glewInit ();
        
        // build and compile our shader programs
        
        // vertex shader
        unsigned int vertexShader = glCreateShader(GL_VERTEX_SHADER);
        glShaderSource(vertexShader, 1, &vertexShaderSource, NULL);
        glCompileShader(vertexShader);
        // check for shader compile errors
        int success;
        char infoLog[512];
        glGetShaderiv(vertexShader, GL_COMPILE_STATUS, &success);
        if (!success)
        {
            glGetShaderInfoLog(vertexShader, 512, NULL, infoLog);
            std::cout << "ERROR::SHADER::VERTEX::COMPILATION_FAILED\n"
                      << infoLog << std::endl;
        }
        
        // fragment shader
        unsigned int fragmentShader = glCreateShader(GL_FRAGMENT_SHADER);
        glShaderSource(fragmentShader, 1, &fragmentShaderSource, NULL);
        glCompileShader(fragmentShader);
        // check for shader compile errors
        glGetShaderiv(fragmentShader, GL_COMPILE_STATUS, &success);
        if (!success)
        {
            glGetShaderInfoLog(fragmentShader, 512, NULL, infoLog);
            std::cout << "ERROR::SHADER::FRAGMENT::COMPILATION_FAILED\n"
                      << infoLog << std::endl;
        }
        
        // link shaders
        unsigned int shaderProgram = glCreateProgram();
        glAttachShader(shaderProgram, vertexShader);
        glAttachShader(shaderProgram, fragmentShader);
        glLinkProgram(shaderProgram);
        // check for linking errors
        glGetProgramiv(shaderProgram, GL_LINK_STATUS, &success);
        if (!success) {
            glGetProgramInfoLog(shaderProgram, 512, NULL, infoLog);
            std::cout << "ERROR::SHADER::PROGRAM::LINKING_FAILED\n"
                      << infoLog << std::endl;
        }
        glDeleteShader(vertexShader);
        glDeleteShader(fragmentShader);
        
        //~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        // TODO 20230219 starting to prototype animation
        float vertices[9];
        //~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        //~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        // TODO 20230224 testing Agent
        Agent agent;
        //~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        unsigned int VBO, VAO;
        glGenVertexArrays(1, &VAO);
        glGenBuffers(1, &VBO);
        
        // uncomment this call to draw in wireframe polygons.
        //glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);
        
        // render loop
        // -----------
        while (!glfwWindowShouldClose(window))
        {
//            sampleVertexArray(frame_count_, vertices);
            sampleVertexArray(agent, frame_count_, vertices);

            // bind the Vertex Array Object first, then bind and set vertex buffer(s),
            // and then configure vertex attributes(s).
            glBindVertexArray(VAO);
            
            glBindBuffer(GL_ARRAY_BUFFER, VBO);
            glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices,
                         GL_STREAM_DRAW);
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE,
                                  3 * sizeof(float), (void*)0);
            glEnableVertexAttribArray(0);
            
            // note that this is allowed, the call to glVertexAttribPointer
            // registered VBO as the vertex attribute's bound vertex buffer object
            // so afterwards we can safely unbind
            glBindBuffer(GL_ARRAY_BUFFER, 0);
            
            // You can unbind the VAO afterwards so other VAO calls won't
            // accidentally modify this VAO, but this rarely happens. Modifying
            // other VAOs requires a call to glBindVertexArray anyways so we
            // generally don't unbind VAOs (nor VBOs) when it's not directly
            // necessary.
            glBindVertexArray(0);
            
            // input
            // -----
            processInput(window);
            
            // render
            // ------
            glClearColor(0.2f, 0.3f, 0.3f, 1.0f);
            glClear(GL_COLOR_BUFFER_BIT);
            
            // draw our first triangle
            glUseProgram(shaderProgram);
            glBindVertexArray(VAO); // seeing as we only have a single VAO there's
            // no need to bind it every time, but we'll do
            // so to keep things a bit more organized
            glDrawArrays(GL_TRIANGLES, 0, 3);
            // glBindVertexArray(0); // no need to unbind it every time
            
            // glfw: swap buffers and poll IO events (keys pressed/released, mouse
            // moved etc.)
            glfwSwapBuffers(window);
            glfwPollEvents();
            
            //~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            // TODO 20230224 testing Agent
//            agent.steer(Vec3(0, 0, 1), 1.0 / 60);
            // TODO 20230225 need to measure elapsed real time?
//            agent.steer(Vec3(0, 0, 5), 1.0 / 60);
//            agent.steer(Vec3(1, 0, 5), 1.0 / 60);
            agent.steer(agent.side() * 20 + agent.forward() * 0.5, 1.0 / 60);

            std::cout << frame_count_ << " s="
                      << agent.getSpeed()
                      << agent.ls() << std::endl;
            
            //~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


            frame_count_++;
        }
        
        std::cout << "frame_count = " << frame_count_ << std::endl;
        
        // optional: de-allocate all resources once they've outlived their purpose:
        glDeleteVertexArrays(1, &VAO);
        glDeleteBuffers(1, &VBO);
        glDeleteProgram(shaderProgram);
        
        // glfw: terminate, clearing all previously allocated GLFW resources.
        glfwTerminate();
        return 0;
    }
    
    //~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    // TODO 20230219 starting to prototype animation
    
//    void sampleVertexArray(int frames, float* xyz3)
//    {
//        // TODO 20230220 clean up. in c++20 it is std::numbers::pi
//        float pi = M_PI;
//        float pi2 = pi * 2;
//
//        Vec3 a = Vec3(0, 0.8, 0).rotateXyAboutZ(frames * 0.01);
//        Vec3 b = a.rotateXyAboutZ(pi2 / 3);
//        Vec3 c = b.rotateXyAboutZ(pi2 / 3);
//
//        int i = 0;
//        xyz3[i++] = a.x();
//        xyz3[i++] = a.y();
//        xyz3[i++] = a.z();
//        xyz3[i++] = b.x();
//        xyz3[i++] = b.y();
//        xyz3[i++] = b.z();
//        xyz3[i++] = c.x();
//        xyz3[i++] = c.y();
//        xyz3[i++] = c.z();
//    }

    void sampleVertexArray(const Agent& agent, int frames, float* xyz3)
    {
        // TODO 20230220 clean up. in c++20 it is std::numbers::pi
        float pi = M_PI;
        float pi2 = pi * 2;
        
//        Vec3 a = Vec3(0, 0.8, 0).rotateXyAboutZ(frames * 0.01);
//        Vec3 b = a.rotateXyAboutZ(pi2 / 3);
//        Vec3 c = b.rotateXyAboutZ(pi2 / 3);
        
//        float scale = 0.08;
//        float scale = 0.008;
        float scale = 0.004;
        float angle = frames * 0.01;
//        Vec3 position(-0.5, 0, 0);
//        Vec3 position = agent.position();
//        Vec3 pan(0, -0.9, 0);
        Vec3 pan(0, 0, 0);
//        Vec3 pan(0, 0.9, 0);
//        Vec3 position = pan + (agent.position() * scale);
//        Vec3 position = pan + (Vec3(0, agent.position().z(), 0) * scale);
        Vec3 fudge_orientation(agent.position().x(), agent.position().z(), 0);
        Vec3 position = pan + (fudge_orientation * scale);

        Vec3 a = Vec3(0, scale, 0).rotateXyAboutZ(angle);
        Vec3 b = a.rotateXyAboutZ(pi2 / 3);
        Vec3 c = b.rotateXyAboutZ(pi2 / 3);
        
        a += position;
        b += position;
        c += position;

        int i = 0;
        xyz3[i++] = a.x();
        xyz3[i++] = a.y();
        xyz3[i++] = a.z();
        xyz3[i++] = b.x();
        xyz3[i++] = b.y();
        xyz3[i++] = b.z();
        xyz3[i++] = c.x();
        xyz3[i++] = c.y();
        xyz3[i++] = c.z();
    }

    //~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    
    // process all input: query GLFW whether relevant keys are pressed/released this
    // frame and react accordingly
    void processInput(GLFWwindow *window)
    {
        if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS)
            glfwSetWindowShouldClose(window, true);
    }
    
    // glfw: whenever the window size changed (by OS or user resize) this callback
    // function executes
    static
    void framebuffer_size_callback(GLFWwindow* window, int width, int height)
    {
        // make sure the viewport matches the new window dimensions; note that width
        // and height will be significantly larger than specified on retina displays.
        glViewport(0, 0, width, height);
    }

    
private:
    int window_width_ = 1000;
    int window_height_ = 1000;
    int frame_count_ = 0;
};
