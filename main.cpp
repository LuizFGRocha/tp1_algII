#include <iostream>
#include <vector>
#include <sstream>
#include <cmath>
#include <algorithm>

struct excecao_pontos_iguais{};

/// @brief Representa um ponto no R^2
class ponto {

  public:

    ponto() {}

    /// @brief Constrói um ponto dadas as suas coordenadas
    /// @param arg_x A coordenada x
    /// @param arg_y A coordenada y
    ponto(float arg_x, float arg_y) : x(arg_x), y(arg_y) {}

    /// @brief Retorna o valor da coordenada x do ponto
    float coordenada_x() const {
        return x;
    }

    /// @brief Retorna o valor da coordenada y do ponto
    float coordenada_y() const {
        return y;
    }

  private:

    float x, y;
};

/// @brief Representa um vértice do grafo.
struct vertice_grafo {
    /// @brief Lista de adjacências do vértice
    std::vector<uint32_t> adjacencias;

    /// @brief Coordenadas do vértice no R^2
    ponto coordenadas;
};

/// @brief Representa um grafo
class grafo {

  public:

    /// @brief Consatrutor padrão. Inicializa a quantidade de faces para -1 para indicar que 
    /// o valor não foi calculado.
    grafo() : quantidade_faces(-1) {}

    /// @brief Vértices do grafo. Cada um tem suas coordenadas e sua lista de adjacência.
    std::vector<vertice_grafo> vertices;

    /// @brief Lista de "visitas" do grafo. A posição [i][j] é true se e somente se a aresta
    /// {i, j} do grafo foi percorrida no sentido de i para j.
    std::vector<std::vector<bool>> percorrido;

    /// @brief A quantidade de faces no grafo. É calculada usando a fórmula de Euler, para
    /// economizar iterações na busca por faces.
    int quantidade_faces;
};

/// @brief Lê os argumentos passados no console
/// @param grafo O grafo que receberá os argumentos
void parse_args(grafo& grafo) {
    std::string linha_atual;

    std::getline(std::cin, linha_atual);
    std::stringstream stream_vertices_arestas(linha_atual);

    uint32_t quantidade_vertices, quantidade_arestas;
    stream_vertices_arestas >> quantidade_vertices >> quantidade_arestas;
    grafo.quantidade_faces = quantidade_arestas - quantidade_vertices + 2; // Fórmula de Euler

    grafo.vertices.resize(quantidade_vertices);
    grafo.percorrido.resize(quantidade_vertices);

    for (int i = 0; std::getline(std::cin, linha_atual); i++) {
        std::stringstream stream_linha_atual(linha_atual);

        float x, y;
        stream_linha_atual >> x >> y;
        grafo.vertices[i].coordenadas = ponto(x, y);

        uint32_t grau;
        stream_linha_atual >> grau;
        grafo.vertices[i].adjacencias.resize(grau);
        grafo.percorrido[i].resize(grau);

        uint32_t vertice_conectado;
        for (int j = 0; stream_linha_atual >> vertice_conectado; j++) {
            grafo.vertices[i].adjacencias[j] = vertice_conectado - 1;
        }
    }
}

/// @brief Calcula o ângulo entre dois pontos
/// @param p O primeiro ponto
/// @param q O segundo ponto
/// @return O double referente ao ângulo, em radianos. Se os pontos estão em uma mesma reta paralela ao eixo x, com p à esquerda, o ângulo é 0.
/// Ele cresce no sentido anti-horário
double angulo(const ponto& p, const ponto& q) {

    double dx = q.coordenada_x() - p.coordenada_x();
    double dy = q.coordenada_y() - p.coordenada_y();

    return atan2(dy, dx);
}

/// @brief Ordena as listas de adjacências de todos os vértices do grafo, tendo como referência
/// o ângulo polar da saída do vértice.
/// @param grafo O grafo cujas listas de adjacências serão ordenadas.
void ordena_adjacencias(grafo& grafo) {
    for (int i = 0; i < grafo.vertices.size(); ++i) {
        auto comparador = [&grafo, i] (uint32_t ponto_1, uint32_t ponto_2) {
            return (angulo(grafo.vertices[i].coordenadas, grafo.vertices[ponto_1].coordenadas) <
                   angulo(grafo.vertices[i].coordenadas, grafo.vertices[ponto_2].coordenadas));
        };

        std::sort(grafo.vertices[i].adjacencias.begin(), grafo.vertices[i].adjacencias.end(), comparador);
    }
}

struct retorno_proximo_vertice {
    uint32_t posicao_universal;
    uint32_t posicao_adjacencia;
};

/// @brief Auxiliar para a busca das faces. Encontra o próximo vértice da face.
/// @param grafo O grafo cujas faces estão sendo encontradas.
/// @param i O vértice anterior.
/// @param j O vértice atual.
/// @return O próximo vértice.
uint32_t pega_posicao_proximo_vertice(grafo& grafo, uint32_t i, uint32_t j) {
    uint32_t posicao_incidencia;
    uint32_t vertice_destino = grafo.vertices[i].adjacencias[j];

    for (int k = 0; k < grafo.vertices[vertice_destino].adjacencias.size(); ++k)
        if (grafo.vertices[vertice_destino].adjacencias[k] == i)
            posicao_incidencia = k;

    return (posicao_incidencia + 1) % grafo.vertices[vertice_destino].adjacencias.size();
}

/// @brief Encontra as faces em um grafo planar conexo
/// @param grafo O grafo no qual as faces serão procuradas
/// @return Retorna um vetor de vetores de inteiros. Cada vetor de inteiros é uma face.
std::vector<std::vector<uint32_t>> encontra_faces(grafo& grafo) {
    std::vector<std::vector<uint32_t>> faces;

    ordena_adjacencias(grafo);

    for (int i = 0; i < grafo.vertices.size(); i++) {
        if (faces.size() >= grafo.quantidade_faces)
            break;

        for (int j = 0; j < grafo.vertices[i].adjacencias.size(); ++j) {
            if (grafo.percorrido[i][j])
                continue;

            std::vector<uint32_t> face;

            uint32_t vertice_inicio = i, vertice_fim = j, proximo_vertice;
            
            while (!grafo.percorrido[vertice_inicio][vertice_fim]) {
                grafo.percorrido[vertice_inicio][vertice_fim] = true;
                face.push_back(vertice_inicio);

                proximo_vertice = pega_posicao_proximo_vertice(grafo, vertice_inicio, vertice_fim);
                vertice_inicio = grafo.vertices[vertice_inicio].adjacencias[vertice_fim];
                vertice_fim = proximo_vertice;
            }
            face.push_back(vertice_inicio);

            faces.push_back(face);
        }
    }

    return faces;
}

/// @brief Imprime as faces no console.
/// @param faces O vetor de vetor de inteiros que codifica as faces
void imprime_faces(std::vector<std::vector<uint32_t>> faces) {
    std::cout << faces.size() << std::endl;
    for (auto face : faces) {
        std::cout << face.size();
        for (auto vertice : face) {
            std::cout << " " << vertice + 1;
        }
        std::cout << std::endl;
    }
}

int main() {
    grafo G;
    parse_args(G);
    imprime_faces(encontra_faces(G));
    return 0;
}
