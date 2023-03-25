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

#include <iostream>     // c++ stream I/O.
#include <vector>       // STL adjustable array.

#include <GL/glew.h>    // Cross platform "OpenGL Extention Wrangler".
#include <GLFW/glfw3.h> // Cross platform library for window management.

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
//        // 20230307 very temp
//        for (int t = 5; t > 0; t--)
//        {
//            using namespace std::chrono_literals;
//            std::this_thread::sleep_for(1000ms);
//            std::cout << t << std::endl;
//        }
        
//        RandomSequence rs;
//        float s = 300 * drawScale();
        float s = 400 * drawScale();
        debugPrint(s);
//        int flock_size = 13;
//        int flock_size = 40;
        int flock_size = 60;
        for (int i = 0; i < flock_size; i++)
        {
//            Vec3 p(rs().frandom2(-s, s), rs().frandom2(-s, s), 0);
            Vec3 p(rs().frandom2(-s, s), rs().frandom2(-s, s), s);
            boids_.push_back(Boid());
            boids_[i].ls().setIJKP(Vec3(1, 0, 0),
                                   Vec3(0, 0, -1),
                                   Vec3(0, 1, 0),
                                   p);
            boids_[i].ls().setIJKP(Vec3(1,0,0), Vec3(0,0,-1), Vec3(0,1,0), p);
        }
//        for (auto& boid : boids_) { debugPrint(boid.ls()); }
        sample_opengl_code();
    }

    // TODO 20230219 just scaffolding to prototype OpenGL drawing code.
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
        window_ = glfwCreateWindow(window_width_, window_height_,
                                   "flock", NULL, NULL);
        if (window_ == NULL)
        {
            std::cout << "Failed to create GLFW window" << std::endl;
            glfwTerminate();
            return -1;
        }
        glfwMakeContextCurrent(window_);
        glfwSetFramebufferSizeCallback(window_, framebuffer_size_callback);
        
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
        shaderProgram_ = glCreateProgram();
        glAttachShader(shaderProgram_, vertexShader);
        glAttachShader(shaderProgram_, fragmentShader);
        glLinkProgram(shaderProgram_);
        // check for linking errors
        glGetProgramiv(shaderProgram_, GL_LINK_STATUS, &success);
        if (!success)
        {
            glGetProgramInfoLog(shaderProgram_, 512, NULL, infoLog);
            std::cout << "ERROR::SHADER::PROGRAM::LINKING_FAILED\n"
                      << infoLog << std::endl;
        }
        glDeleteShader(vertexShader);
        glDeleteShader(fragmentShader);
        
        glGenVertexArrays(1, &VAO_);
        glGenBuffers(1, &VBO_);
        
        // uncomment this call to draw in wireframe polygons.
        //glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);
        
        // render loop
        while (!glfwWindowShouldClose(window_)) { drawFrame(); }

        std::cout << "frame_count = " << frame_count_ << std::endl;
        
        // TODO 20230227 these should all be in the ~Draw() destructor.
        // optional: de-allocate all resources once they've outlived their purpose:
        glDeleteVertexArrays(1, &VAO_);
        glDeleteBuffers(1, &VBO_);
        glDeleteProgram(shaderProgram_);
        // glfw: terminate, clearing all previously allocated GLFW resources.
        glfwTerminate();
        
        return 0;
    }
    
    // TODO maybe call this drawScene() ?
    void drawFrame()
    {
        vboDataClear();
        sampleVertexArray();

        // bind the Vertex Array Object first, then bind and set vertex buffer(s),
        // and then configure vertex attributes(s).
        glBindVertexArray(VAO_);
                
        glBindBuffer(GL_ARRAY_BUFFER, VBO_);
        glBufferData(GL_ARRAY_BUFFER,
                     vboDataBytes(),
                     vboData().data(),
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
        processInput(window_);

        // render
        glClearColor(0.2f, 0.3f, 0.3f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);
        
        // draw our first triangle
        glUseProgram(shaderProgram_);
        glBindVertexArray(VAO_); // seeing as we only have a single VAO there's
                                 // no need to bind it every time, but we'll do
                                 // so to keep things a bit more organized

        // Draw triangles (as 3*t vertices).
        glDrawArrays(GL_TRIANGLES, 0, triangle_count_ * 3);

        // glBindVertexArray(0); // no need to unbind it every time
        
        // glfw: swap buffers and poll IO events (keys pressed/released, mouse
        // moved etc.)
        glfwSwapBuffers(window_);
        glfwPollEvents();
        
        // Advance each boid by onem simulation step.
        for (auto& boid : boids_)
        {
            // TODO 20230225 need to measure elapsed real time?
            float dt = 1.0 / 60.0;
//            boid.steer(boid.side() * 20 + (boid.forward() * 0.5), dt);
//            boid.steer(boid.wanderSteer(rs(), dt) * 0.01, dt);
            boid.steer(boid.wanderSteer(rs()) * 0.01, dt);
        }
        frame_count_++;
    }
    
    // TODO 20230219 starting to prototype animation
    void sampleVertexArray()
    {
        for (auto& boid : boids_) { addBoidToScene(boid); }
    }

    void addBoidToScene(const Agent& agent)
    {
        float boid_size = 0.5;
        Vec3 position = agent.position();
        Vec3 nose_offset = agent.forward() * boid_size;
        Vec3 wing_offset = agent.side() * boid_size;
        Vec3 nose  = (position + nose_offset              ) * drawScale();
        Vec3 wing1 = (position - nose_offset + wing_offset) * drawScale();
        Vec3 wing2 = (position - nose_offset - wing_offset) * drawScale();
        addTriangle(nose, wing1, wing2);
    }

    // TODO should this be addTriangleToVBO() ?
    void addTriangle(const Vec3& a, const Vec3& b, const Vec3& c)
    {
        addVertex(a);
        addVertex(b);
        addVertex(c);
        triangle_count_++;
    }
    
    void addVertex(const Vec3& v)
    {
        vboData().push_back(v.x());
        vboData().push_back(v.y());
        vboData().push_back(v.z());
    }
    
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

    // Wrappers for OpenGL VBO.
    const std::vector<float>& vboData() const { return vbo_data_; }
    std::vector<float>& vboData() { return vbo_data_; }
    unsigned int vboDataBytes() { return vboData().size() * sizeof(float); }
    void vboDataClear()
    {
        vboData().clear();
        triangle_count_ = 0;
    }

    float drawScale() const { return draw_scale_; }
    
    RandomSequence& rs() { return rs_; }


private:
//    int window_width_ = 1000;
//    int window_height_ = 1000;
    int window_width_ = 500;
    int window_height_ = 500;
    int frame_count_ = 0;
    
    // Overall draw scale, to be replaced by 3d camera model.
    float draw_scale_ = 0.04;

    unsigned int VAO_;
    unsigned int VBO_;

    // Pointer to window created by GLFW
    GLFWwindow* window_ = nullptr;

    // ID for triangle shader program.
    unsigned int shaderProgram_;
    
    // code from https://learnopengl.com/Getting-started/Hello-Triangle
    const char *vertexShaderSource =
         "#version 330 core                                   \
         layout (location = 0) in vec3 aPos;                  \
         void main()                                          \
         {                                                    \
             gl_Position = vec4(aPos.x, aPos.y, aPos.z, 1.0); \
         }";
    
    const char *fragmentShaderSource =
         "#version 330 core                            \
         out vec4 FragColor;                           \
         void main()                                   \
         {                                             \
             FragColor = vec4(1.0f, 0.5f, 0.2f, 1.0f); \
         }";
    
    // Holds float data for VBO. Refilled each draw step.
    std::vector<float> vbo_data_;
    
    // Per frame count of triangles added to scene.
    int triangle_count_ = 0;

    RandomSequence rs_;

    // Flock of boids.
    std::vector<Boid> boids_;
};
