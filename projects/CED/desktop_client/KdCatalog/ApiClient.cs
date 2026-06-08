// Copyright 2026 Rinat Ishmaev
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text.Json.Serialization;

namespace KdCatalog;

public sealed class ApiClient
{
    private readonly HttpClient _httpClient = new();
    private string _accessToken = string.Empty;
    private string _refreshToken = string.Empty;

    public string CurrentRole { get; private set; } = "user";

    public void Configure(string baseUrl)
    {
        _httpClient.BaseAddress = new Uri(baseUrl.TrimEnd('/') + "/");
    }

    public async Task LoginAsync(string login, string password)
    {
        var response = await _httpClient.PostAsJsonAsync("auth/login", new { login, password });
        response.EnsureSuccessStatusCode();
        var json = await response.Content.ReadFromJsonAsync<TokenPairDto>();
        if (json is null) return;
        _accessToken = json.AccessToken;
        _refreshToken = json.RefreshToken;
        _httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", _accessToken);
        var me = await _httpClient.GetFromJsonAsync<UserMeDto>("auth/me");
        CurrentRole = me?.Role ?? "user";
    }

    public async Task<IReadOnlyList<CatalogRowDto>> GetCatalogAsync(string? docNumber = null, string? name = null)
    {
        var query = $"catalog?page=1&size=500";
        if (!string.IsNullOrWhiteSpace(docNumber)) query += $"&doc_number={Uri.EscapeDataString(docNumber)}";
        if (!string.IsNullOrWhiteSpace(name)) query += $"&name={Uri.EscapeDataString(name)}";
        var payload = await _httpClient.GetFromJsonAsync<CatalogResponseDto>(query);
        return payload?.Items ?? Array.Empty<CatalogRowDto>();
    }

    public async Task ProcessInboxAsync()
    {
        var response = await _httpClient.PostAsync("inbox/process", null);
        response.EnsureSuccessStatusCode();
    }

    public async Task ExportCatalogAsync()
    {
        var response = await _httpClient.GetAsync("catalog/export");
        response.EnsureSuccessStatusCode();
        var bytes = await response.Content.ReadAsByteArrayAsync();
        var path = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), "catalog_export.xlsx");
        await File.WriteAllBytesAsync(path, bytes);
    }

    public async Task<IReadOnlyList<UserRowDto>> GetUsersAsync()
    {
        var rows = await _httpClient.GetFromJsonAsync<List<UserRowDto>>("admin/users");
        return rows ?? new List<UserRowDto>();
    }

    public async Task<IReadOnlyList<RevisionRowDto>> GetHistoryAsync(int documentId)
    {
        var rows = await _httpClient.GetFromJsonAsync<List<RevisionRowDto>>($"records/document/{documentId}/history");
        return rows ?? new List<RevisionRowDto>();
    }

    public async Task<IReadOnlyList<ProviderRowDto>> GetProvidersAsync()
    {
        var rows = await _httpClient.GetFromJsonAsync<List<ProviderRowDto>>("admin/ai-providers");
        return rows ?? new List<ProviderRowDto>();
    }

    public async Task CreateProviderAsync(ProviderPayloadDto payload)
    {
        var response = await _httpClient.PostAsJsonAsync("admin/ai-providers", payload);
        response.EnsureSuccessStatusCode();
    }

    public async Task UpdateProviderAsync(int id, ProviderPayloadDto payload)
    {
        var response = await _httpClient.PutAsJsonAsync($"admin/ai-providers/{id}", payload);
        response.EnsureSuccessStatusCode();
    }

    public async Task<string> AnalyzeDocumentAsync(int documentId)
    {
        var response = await _httpClient.PostAsync($"documents/{documentId}/analyze", null);
        response.EnsureSuccessStatusCode();
        var json = await response.Content.ReadFromJsonAsync<Dictionary<string, object>>();
        return json?.GetValueOrDefault("data")?.ToString() ?? "Анализ завершён";
    }

    public async Task OpenDocumentFileAsync(int documentId, string savePath)
    {
        var response = await _httpClient.GetAsync($"documents/{documentId}/file");
        response.EnsureSuccessStatusCode();
        await using var stream = await response.Content.ReadAsStreamAsync();
        await using var file = File.Create(savePath);
        await stream.CopyToAsync(file);
    }

    private sealed record TokenPairDto(
        [property: JsonPropertyName("access_token")] string AccessToken,
        [property: JsonPropertyName("refresh_token")] string RefreshToken);

    private sealed record CatalogResponseDto(
        [property: JsonPropertyName("items")] CatalogRowDto[] Items,
        [property: JsonPropertyName("total_count")] int TotalCount);

    private sealed record UserMeDto(
        [property: JsonPropertyName("role")] string Role);
}

public sealed class CatalogRowDto
{
    [JsonPropertyName("id")]
    public int Id { get; set; }
    [JsonPropertyName("doc_number")]
    public string DocNumber { get; set; } = "";
    [JsonPropertyName("name")]
    public string Name { get; set; } = "";
    [JsonPropertyName("product_number")]
    public string? ProductNumber { get; set; }
    [JsonPropertyName("status")]
    public string Status { get; set; } = "";
    [JsonPropertyName("ai_status")]
    public AiStatusDto? AiStatus { get; set; }
    [JsonPropertyName("ai_insight")]
    public string? AiInsight { get; set; }
}

public sealed class AiStatusDto
{
    [JsonPropertyName("label")]
    public string Label { get; set; } = "";
    [JsonPropertyName("code")]
    public string Code { get; set; } = "";
}

public sealed class UserRowDto
{
    [JsonPropertyName("login")]
    public string Login { get; set; } = "";
    [JsonPropertyName("role")]
    public string Role { get; set; } = "";
    [JsonPropertyName("department")]
    public string? Department { get; set; }
}

public sealed class RevisionRowDto
{
    [JsonPropertyName("action")]
    public string Action { get; set; } = "";
    [JsonPropertyName("timestamp")]
    public DateTime Timestamp { get; set; }
}
