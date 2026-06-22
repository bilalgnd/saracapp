package com.bilalgnd.saracapp

import android.content.Context
import android.content.Intent
import android.net.Uri
import org.json.JSONObject
import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.setContent
import androidx.compose.animation.animateColorAsState
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.material3.TabRowDefaults.tabIndicatorOffset
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.google.gson.Gson
import com.google.gson.annotations.SerializedName
import com.google.gson.reflect.TypeToken
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.*
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.POST
import java.text.SimpleDateFormat
import java.util.Date
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.systemBarsPadding
import androidx.compose.foundation.combinedClickable
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.layout.offset
import java.util.Locale
import androidx.compose.foundation.border
import androidx.compose.ui.text.TextStyle

data class Secenek(@SerializedName("gr") val gramaj: String, val fiyat: Int)
data class Urun(val ad: String, val secenekler: List<Secenek>)

data class SiparisKalemi(
    @SerializedName("ad") val urunAd: String,
    @SerializedName("gramaj") val detay: String,
    val fiyat: Int,
    val notlar: String
)

data class Adisyon(
    @SerializedName("musteri_adi") val musteriAdi: String,
    val saat: String,
    val kalemler: List<SiparisKalemi>,
    @SerializedName("toplam_tutar") val toplamTutar: Int,
    val durum: String = "Bekliyor",
    val renk: String? = null
)

data class MenuResponse(
    val et: List<Urun>,
    val tavuk: List<Urun>,
    val kampanya: List<Urun>,
    val icecekler: List<Urun>,
    val ekstralar: Map<String, Int>
)

interface KasaApi {
    @retrofit2.http.GET("menu")
    suspend fun menuGetir(): retrofit2.Response<MenuResponse>

    @POST("siparis")
    suspend fun siparisGonder(@Body adisyon: Adisyon): retrofit2.Response<Void>

    @POST("hesap_kapat")
    suspend fun hesapKapat(@Body request: Map<String, String>): retrofit2.Response<Void>

    @POST("yazdir")
    suspend fun yazdir(@Body request: Map<String, String>): retrofit2.Response<Void>
}

object ApiClient {
    private var retrofit: Retrofit? = null
    fun getApi(ip: String): KasaApi {
        val temizIp = ip.trim().ifEmpty { "127.0.0.1" }
        val baseUrl = "http://$temizIp/"
        
        var r = retrofit
        if (r == null || r.baseUrl().host != temizIp) {
            r = try {
                Retrofit.Builder().baseUrl(baseUrl).addConverterFactory(GsonConverterFactory.create()).build()
            } catch (e: Exception) {
                Retrofit.Builder().baseUrl("http://127.0.0.1/").addConverterFactory(GsonConverterFactory.create()).build()
            }
            retrofit = r
        }
        return r!!.create(KasaApi::class.java)
    }
}

class HafizaYoneticisi(context: Context) {
    private val defter = context.getSharedPreferences("SaracogluDefteri", Context.MODE_PRIVATE)
    private val gson = Gson()

    fun kasaIpKaydet(ip: String) {
        val finalIp = if (ip.isNotBlank() && !ip.contains(":")) "$ip:5000" else ip
        defter.edit().putString("KASA_IP", finalIp).apply()
    }
    fun kasaIpOku(): String = defter.getString("KASA_IP", "") ?: ""

    fun garsonRengiKaydet(renk: String) = defter.edit().putString("GARSON_RENGI", renk).apply()
    fun garsonRengiOku(): String = defter.getString("GARSON_RENGI", "#FFFFFF") ?: "#FFFFFF"



    fun cevrimdisiSiparisEkle(adisyon: Adisyon) {
        val liste = cevrimdisiSiparisleriGetir().toMutableList()
        liste.add(adisyon)
        defter.edit().putString("OFFLINE_QUEUE", gson.toJson(liste)).apply()
    }
    fun cevrimdisiSiparisleriGetir(): List<Adisyon> {
        val json = defter.getString("OFFLINE_QUEUE", "[]")
        return gson.fromJson(json, object : TypeToken<List<Adisyon>>() {}.type) ?: emptyList()
    }
    fun cevrimdisiSiparisTemizle() = defter.edit().remove("OFFLINE_QUEUE").apply()

    fun aktifMasalariKaydet(liste: List<Adisyon>) = defter.edit().putString("AKTIF_MASALAR", gson.toJson(liste)).apply()
    fun aktifMasalariGetir(): List<Adisyon> {
        val json = defter.getString("AKTIF_MASALAR", "[]")
        return gson.fromJson(json, object : TypeToken<List<Adisyon>>() {}.type) ?: emptyList()
    }
}

val malzemeler_listesi = listOf("Soğan", "Domates", "Patates", "Ketçap", "Mayonez", "Turşu")
val ucretsiz_ekstra_listesi = listOf("Sade Et", "Soslu", "Gemi", "Kayık")
val odeme_listesi = listOf("POS", "NAKİT", "Paket", "Dükkan içi")

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            MaterialTheme(colorScheme = darkColorScheme(background = Color(0xFF0F0F0F), surface = Color(0xFF1E1E1E), primary = Color(0xFFFF9800), onPrimary = Color.White)) {
                Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) { AnaEkran() }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class, ExperimentalFoundationApi::class)
@Composable
fun AnaEkran() {
    val context = LocalContext.current
    val haptic = LocalHapticFeedback.current
    val hafiza = remember { HafizaYoneticisi(context) }
    val coroutineScope = rememberCoroutineScope()

    var etMenusu by remember { mutableStateOf<List<Urun>>(emptyList()) }
    var tavukMenusu by remember { mutableStateOf<List<Urun>>(emptyList()) }
    var kampanyaMenusu by remember { mutableStateOf<List<Urun>>(emptyList()) }
    var iceceklerMenusu by remember { mutableStateOf<List<Urun>>(emptyList()) }
    var ucretliEkstralar by remember { mutableStateOf<Map<String, Int>>(emptyMap()) }

    var siparisIcinAcilanUrun by remember { mutableStateOf<Urun?>(null) }
    var notDuzenlenecekKalem by remember { mutableStateOf<Pair<Adisyon, SiparisKalemi>?>(null) }

    val aktifSiparisler = remember { mutableStateListOf<Adisyon>().apply { addAll(hafiza.aktifMasalariGetir()) } }
    var siparisEkraniAcik by remember { mutableStateOf(false) }
    var aktifMasaAdi by remember { mutableStateOf<String?>(null) }
    val taslakKalemler = remember { mutableStateListOf<SiparisKalemi>() }
    var duzenlenenAdisyonIsmi by remember { mutableStateOf<String?>(null) }
    var guncellemeUrl by remember { mutableStateOf<String?>(null) }

    var kasaAyarPenceresiAcik by remember { mutableStateOf(false) }

    val sekmeler = listOf("🥩" to "ET DÖNER", "🍗" to "TAVUK DÖNER", "🌟" to "KAMPANYA", "🥤" to "İÇECEKLER")
    val menuler_listesi = listOf(etMenusu, tavukMenusu, kampanyaMenusu, iceceklerMenusu)
    val pagerState = rememberPagerState(pageCount = { sekmeler.size })
    var kasaOnline by remember { mutableStateOf(false) }

    LaunchedEffect(Unit) {
        val client = OkHttpClient()
        var activeWebSocket: WebSocket? = null

        while (true) {
            val ip = hafiza.kasaIpOku().trim()
            if (ip.isNotBlank()) {
                try {
                    val api = ApiClient.getApi(ip)
                    val menuRes = api.menuGetir()
                    if (menuRes.isSuccessful && menuRes.body() != null) {
                        val body = menuRes.body()!!
                        etMenusu = body.et
                        tavukMenusu = body.tavuk
                        kampanyaMenusu = body.kampanya
                        iceceklerMenusu = body.icecekler
                        ucretliEkstralar = body.ekstralar
                    }
                } catch (e: Exception) { }

                val bekleyenler = hafiza.cevrimdisiSiparisleriGetir()
                if (bekleyenler.isNotEmpty() && kasaOnline) {
                    try {
                        val api = ApiClient.getApi(ip)
                        bekleyenler.forEach { api.siparisGonder(it) }
                        hafiza.cevrimdisiSiparisTemizle()
                        withContext(Dispatchers.Main) { Toast.makeText(context, "✅ Bekleyen Siparişler Gitti!", Toast.LENGTH_SHORT).show() }
                    } catch (e: Exception) { }
                }

                if (activeWebSocket == null) {
                    val request = Request.Builder().url("ws://$ip/ws").build()
                    activeWebSocket = client.newWebSocket(request, object : WebSocketListener() {
                        override fun onOpen(webSocket: WebSocket, response: Response) { kasaOnline = true }
                        override fun onMessage(webSocket: WebSocket, text: String) {
                            try {
                                if (text.trim().startsWith("{")) {
                                    val jsonObj = JSONObject(text)
                                    if (jsonObj.has("type") && jsonObj.getString("type") == "apk_guncelleme") {
                                        guncellemeUrl = jsonObj.getString("url")
                                    }
                                } else {
                                    val gelenListe: List<Adisyon> = Gson().fromJson(text, object : TypeToken<List<Adisyon>>() {}.type)
                                    CoroutineScope(Dispatchers.Main).launch {
                                        aktifSiparisler.clear(); aktifSiparisler.addAll(gelenListe); hafiza.aktifMasalariKaydet(gelenListe)
                                    }
                                }
                            } catch (e: Exception) {}
                        }
                        override fun onClosed(webSocket: WebSocket, code: Int, reason: String) { kasaOnline = false; activeWebSocket = null }
                        override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) { kasaOnline = false; activeWebSocket = null }
                    })
                } else { activeWebSocket?.send("ping") }
            }
            delay(3000)
        }
    }

    BackHandler(enabled = siparisEkraniAcik || aktifMasaAdi != null) {
        if (aktifMasaAdi != null) { aktifMasaAdi = null; taslakKalemler.clear(); duzenlenenAdisyonIsmi = null }
        else if (siparisEkraniAcik) siparisEkraniAcik = false
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        if (aktifMasaAdi != null) Text("$aktifMasaAdi İlave", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 24.sp)
                        else if (siparisEkraniAcik) Text("Açık Masalar", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 24.sp)
                        else {
                            Text("SARAÇOĞLU DÖNER", color = Color(0xFFFF9800), fontWeight = FontWeight.ExtraBold, fontSize = 26.sp, letterSpacing = 1.sp, modifier = Modifier.pointerInput(Unit) { detectTapGestures(onLongPress = { kasaAyarPenceresiAcik = true }) })
                        }
                        if (aktifMasaAdi == null && !siparisEkraniAcik) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                if (kasaOnline) Text("🟢 Kasa Bağlı", color = Color(0xFF4CAF50), fontSize = 14.sp)
                                else Text("🔴 Kasa Çevrimdışı", color = Color(0xFFF44336), fontSize = 14.sp)
                                val beklemeSayisi = hafiza.cevrimdisiSiparisleriGetir().size
                                if (beklemeSayisi > 0) Text(" • ⏳ $beklemeSayisi Bekleyen", color = Color.Yellow, fontSize = 14.sp)
                            }
                        }
                    }
                },
                navigationIcon = { if (siparisEkraniAcik) TextButton(onClick = { siparisEkraniAcik = false }) { Text("< Geri", color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Bold) } },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = if (aktifMasaAdi != null) Color(0xFFE65100) else Color(0xFF121212))
            )
        },
        bottomBar = {
            if (aktifMasaAdi != null) {
                BottomAppBar(containerColor = Color(0xFFE65100), contentPadding = PaddingValues(horizontal = 16.dp, vertical = 12.dp), modifier = Modifier.height(80.dp)) {
                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                        Column(modifier = Modifier.weight(1f).padding(end = 8.dp)) {
                            Text("Masa: $aktifMasaAdi", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 20.sp, maxLines = 1, overflow = TextOverflow.Ellipsis)
                            Text("${taslakKalemler.size} Ürün - ${taslakKalemler.sumOf { it.fiyat }} ₺", color = Color.White, fontSize = 13.sp)
                        }
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            TextButton(onClick = { aktifMasaAdi = null; taslakKalemler.clear(); duzenlenenAdisyonIsmi = null }) { Text("İptal", color = Color.White, fontSize = 15.sp) }
                            Spacer(modifier = Modifier.width(12.dp))
                            Button(onClick = {
                                if (taslakKalemler.isNotEmpty()) {
                                    val adisyon = Adisyon(aktifMasaAdi!!, SimpleDateFormat("HH:mm", Locale.getDefault()).format(Date()), taslakKalemler.toList(), taslakKalemler.sumOf { it.fiyat }, renk = hafiza.garsonRengiOku())
                                    CoroutineScope(Dispatchers.IO).launch {
                                        try {
                                            if (!kasaOnline) throw Exception("Offline")
                                            if (ApiClient.getApi(hafiza.kasaIpOku()).siparisGonder(adisyon).isSuccessful)
                                                withContext(Dispatchers.Main) { Toast.makeText(context, "✅ Kasaya Gitti!", Toast.LENGTH_SHORT).show() }
                                            else throw Exception("Hata")
                                        } catch (e: Exception) {
                                            hafiza.cevrimdisiSiparisEkle(adisyon)
                                            withContext(Dispatchers.Main) { Toast.makeText(context, "Kasa Çevrimdışı! Sipariş Kaydedildi.", Toast.LENGTH_LONG).show()
                                                val idx = aktifSiparisler.indexOfFirst { it.musteriAdi == duzenlenenAdisyonIsmi }
                                                if (idx != -1) aktifSiparisler[idx] = adisyon else aktifSiparisler.add(adisyon)
                                                hafiza.aktifMasalariKaydet(aktifSiparisler)
                                            }
                                        }
                                    }
                                }
                                aktifMasaAdi = null; taslakKalemler.clear(); duzenlenenAdisyonIsmi = null
                            }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2E7D32)), modifier = Modifier.height(56.dp)) { Text(if(kasaOnline) "Siparişi Gönder" else "Telefona Kaydet", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 15.sp) }
                        }
                    }
                }
            }
        },
        floatingActionButton = {
            if (!siparisEkraniAcik && aktifSiparisler.isNotEmpty() && aktifMasaAdi == null) {
                ExtendedFloatingActionButton(onClick = { siparisEkraniAcik = true }, containerColor = Color(0xFFD84315), contentColor = Color.White) { Text("Masalar (${aktifSiparisler.size})", fontWeight = FontWeight.Bold, fontSize = 20.sp) }
            }
        }
    ) { paddingValues ->
        Column(modifier = Modifier.fillMaxSize().padding(paddingValues)) {
            if (!siparisEkraniAcik) {
                TabRow(
                    selectedTabIndex = pagerState.currentPage, containerColor = Color(0xFF0F0F0F), contentColor = Color.White,
                    indicator = { tabPositions -> TabRowDefaults.Indicator(Modifier.tabIndicatorOffset(tabPositions[pagerState.currentPage]), color = Color(0xFFFF9800), height = 4.dp) }
                ) {
                    sekmeler.forEachIndexed { index, sekme ->
                        Tab(selected = pagerState.currentPage == index, onClick = { coroutineScope.launch { pagerState.animateScrollToPage(index) } }, 
                            icon = { Text(sekme.first, fontSize = 24.sp) },
                            text = { Text(sekme.second, fontSize = 10.sp, fontWeight = if (pagerState.currentPage == index) FontWeight.Bold else FontWeight.Medium, color = if (pagerState.currentPage == index) Color(0xFFFF9800) else Color.LightGray, textAlign = TextAlign.Center, maxLines = 1, overflow = TextOverflow.Ellipsis) })
                    }
                }
            }

            if (siparisEkraniAcik) {
                LazyColumn(verticalArrangement = Arrangement.spacedBy(16.dp), contentPadding = PaddingValues(16.dp)) {
                    items(aktifSiparisler) { adisyon ->
                        AdisyonKarti(
                            adisyon = adisyon,
                            tamamlandiClick = {
                                aktifSiparisler.removeAll { it.musteriAdi == adisyon.musteriAdi }; hafiza.aktifMasalariKaydet(aktifSiparisler)
                                CoroutineScope(Dispatchers.IO).launch { try { ApiClient.getApi(hafiza.kasaIpOku()).hesapKapat(mapOf("musteri_adi" to adisyon.musteriAdi)) } catch (e: Exception) {} }
                            },
                            kalemSilClick = { silinmekIstenenKalem -> 
                                val orderIndex = aktifSiparisler.indexOfFirst { it.musteriAdi == adisyon.musteriAdi }
                                if (orderIndex != -1) {
                                    val yeniKalemler = aktifSiparisler[orderIndex].kalemler.toMutableList()
                                    yeniKalemler.remove(silinmekIstenenKalem) 
                                    
                                    if (yeniKalemler.isEmpty()) {
                                        aktifSiparisler.removeAt(orderIndex)
                                        hafiza.aktifMasalariKaydet(aktifSiparisler)
                                        if (kasaOnline) CoroutineScope(Dispatchers.IO).launch { try { ApiClient.getApi(hafiza.kasaIpOku()).hesapKapat(mapOf("musteri_adi" to adisyon.musteriAdi)) } catch (e: Exception) {} }
                                    } else {
                                        aktifSiparisler[orderIndex] = aktifSiparisler[orderIndex].copy(kalemler = yeniKalemler, toplamTutar = yeniKalemler.sumOf { it.fiyat })
                                        hafiza.aktifMasalariKaydet(aktifSiparisler)
                                        if (kasaOnline) CoroutineScope(Dispatchers.IO).launch { try { ApiClient.getApi(hafiza.kasaIpOku()).siparisGonder(aktifSiparisler[orderIndex]) } catch (e: Exception) {} }
                                    }
                                }
                            },
                            ilaveClick = { aktifMasaAdi = adisyon.musteriAdi; taslakKalemler.clear(); taslakKalemler.addAll(adisyon.kalemler); duzenlenenAdisyonIsmi = adisyon.musteriAdi; siparisEkraniAcik = false },
                            notDuzenleClick = { kalem -> notDuzenlenecekKalem = Pair(adisyon, kalem) },
                            yazdirClick = {
                                if (kasaOnline) CoroutineScope(Dispatchers.IO).launch { try { ApiClient.getApi(hafiza.kasaIpOku()).yazdir(mapOf("musteri_adi" to adisyon.musteriAdi)) } catch (e: Exception) {} }
                                else Toast.makeText(context, "Kasa çevrimdışı!", Toast.LENGTH_LONG).show()
                            }
                        )
                    }
                }
            } else {
                HorizontalPager(state = pagerState, modifier = Modifier.fillMaxSize()) { sayfaIndexi ->
                    LazyVerticalGrid(columns = GridCells.Fixed(2), verticalArrangement = Arrangement.spacedBy(16.dp), horizontalArrangement = Arrangement.spacedBy(16.dp), contentPadding = PaddingValues(start = 16.dp, end = 16.dp, top = 16.dp, bottom = 100.dp)) {
                        items(menuler_listesi[sayfaIndexi]) { urun -> UrunKarti(urun, onClick = { siparisIcinAcilanUrun = urun }, onLongClick = { }) }
                    }
                }
            }
        }

        if (notDuzenlenecekKalem != null) {
            val (adisyon, kalem) = notDuzenlenecekKalem!!
            var yeniNot by remember { mutableStateOf(kalem.notlar) }
            AlertDialog(
                onDismissRequest = { notDuzenlenecekKalem = null }, containerColor = Color(0xFF242424),
                title = { Text("Not Düzenle", color = Color.White, fontSize = 22.sp, fontWeight = FontWeight.Bold) },
                text = { OutlinedTextField(value = yeniNot, onValueChange = { yeniNot = it }, label = { Text("Örn: Çok pişsin") }, modifier = Modifier.fillMaxWidth(), textStyle = androidx.compose.ui.text.TextStyle(fontSize = 15.sp)) },
                confirmButton = {
                    Button(onClick = {
                        val adisyonIndex = aktifSiparisler.indexOfFirst { it.musteriAdi == adisyon.musteriAdi }
                        if (adisyonIndex != -1) {
                            val yeniKalemler = aktifSiparisler[adisyonIndex].kalemler.toMutableList()
                            val kalemIndex = yeniKalemler.indexOf(kalem)
                            if (kalemIndex != -1) {
                                yeniKalemler[kalemIndex] = yeniKalemler[kalemIndex].copy(notlar = yeniNot.trim())
                                aktifSiparisler[adisyonIndex] = aktifSiparisler[adisyonIndex].copy(kalemler = yeniKalemler)
                                hafiza.aktifMasalariKaydet(aktifSiparisler)
                                if(kasaOnline) CoroutineScope(Dispatchers.IO).launch { try { ApiClient.getApi(hafiza.kasaIpOku()).siparisGonder(aktifSiparisler[adisyonIndex]) } catch (e: Exception) {} }
                            }
                        }
                        notDuzenlenecekKalem = null
                    }) { Text("Kaydet", fontSize = 15.sp) }
                },
                dismissButton = { TextButton(onClick = { notDuzenlenecekKalem = null }) { Text("İptal", fontSize = 15.sp, color = Color.LightGray) } }
            )
        }

        if (guncellemeUrl != null) {
            AlertDialog(
                onDismissRequest = { },
                containerColor = Color(0xFF242424),
                title = { Text("📢 Yeni Güncelleme!", color = Color.White, fontSize = 22.sp, fontWeight = FontWeight.Bold) },
                text = { Text("Kasa tarafından yeni bir Android sürümü yayınlandı. İndirip kurmak ister misiniz?", color = Color.LightGray, fontSize = 15.sp) },
                confirmButton = {
                    Button(onClick = {
                        val i = Intent(Intent.ACTION_VIEW, Uri.parse(guncellemeUrl))
                        context.startActivity(i)
                        guncellemeUrl = null
                    }, colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF4CAF50))) {
                        Text("İndir", fontSize = 15.sp, color = Color.White, fontWeight = FontWeight.Bold)
                    }
                },
                dismissButton = {
                    TextButton(onClick = { guncellemeUrl = null }) {
                        Text("Daha Sonra", fontSize = 15.sp, color = Color.Gray)
                    }
                }
            )
        }

        if (kasaAyarPenceresiAcik) {
            var ipGirdisi by remember { mutableStateOf(hafiza.kasaIpOku()) }
            var renkGirdisi by remember { mutableStateOf(hafiza.garsonRengiOku()) }
            AlertDialog(onDismissRequest = { kasaAyarPenceresiAcik = false }, containerColor = Color(0xFF242424), title = { Text("⚙️ Ayarlar", color = Color.White, fontSize = 22.sp) },
                text = {
                    Column {
                        OutlinedTextField(value = ipGirdisi, onValueChange = { ipGirdisi = it }, label = { Text("Kasa IP Adresi", color = Color.Gray) }, textStyle = androidx.compose.ui.text.TextStyle(color = Color.White, fontSize = 15.sp), singleLine = true, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Uri))
                        Spacer(Modifier.height(16.dp))
                        Text("Garson Rengi", color = Color.White, fontSize = 13.sp)
                        @OptIn(ExperimentalLayoutApi::class)
                        FlowRow(modifier = Modifier.padding(top = 8.dp), horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            listOf("#F44336", "#9C27B0", "#2196F3", "#4CAF50", "#FFC107", "#FF9800", "#795548", "#FFFFFF").forEach { hex ->
                                Box(modifier = Modifier.size(36.dp).background(Color(android.graphics.Color.parseColor(hex)), CircleShape).border(if (renkGirdisi == hex) 3.dp else 0.dp, Color.White, CircleShape).clickable { renkGirdisi = hex })
                            }
                        }
                        Spacer(Modifier.height(24.dp))
                        Text("v4.1.1 | Credits: bilalgnd", color = Color.DarkGray, fontSize = 12.sp, modifier = Modifier.align(Alignment.CenterHorizontally))
                    }
                },
                confirmButton = { Button(onClick = { hafiza.kasaIpKaydet(ipGirdisi.trim()); hafiza.garsonRengiKaydet(renkGirdisi); kasaAyarPenceresiAcik = false }) { Text("Kaydet", fontSize = 15.sp) } },
                dismissButton = { TextButton(onClick = { kasaAyarPenceresiAcik = false }) { Text("İptal", fontSize = 15.sp, color = Color.Gray) } }
            )
        }



        if (siparisIcinAcilanUrun != null) {
            SiparisBottomSheet(
                urun = siparisIcinAcilanUrun!!, guncelMasaAdi = aktifMasaAdi, icecekMenusu = iceceklerMenusu, ucretliEkstralar = ucretliEkstralar, kapat = { siparisIcinAcilanUrun = null },
                onSiparisEkle = { isim, kalemler ->
                    haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                    var sonIsim = isim
                    if (aktifMasaAdi == null) {
                        aktifMasaAdi = sonIsim
                    }
                    taslakKalemler.addAll(kalemler); siparisIcinAcilanUrun = null
                }
            )
        }
    }
}

@Composable
fun UrunKarti(urun: Urun, onClick: () -> Unit, onLongClick: () -> Unit) {
    val adLc = urun.ad.lowercase()
    val bgRenk = when {
        adLc.contains("tombik") -> Color(0xFFFF9800)
        adLc.contains("eski usul") -> Color(0xFFF44336)
        adLc.contains("durum") -> Color(0xFFFFEB3B)
        adLc.contains("et porsiyon") || adLc.contains("beyti") || adLc.contains("iskender") || adLc.contains("ıskender") || (adLc.contains("pilav ustu") && !adLc.contains("tavuk")) -> Color(0xFF8B0000)
        adLc.contains("hatay") -> Color(0xFFF5DEB3)
        adLc.contains("biga") -> Color(0xFF1976D2)
        adLc.contains("tavuk porsiyon") || (adLc.contains("pilav ustu") && adLc.contains("tavuk")) -> Color(0xFFFF5722)
        else -> Color(0xFF242424)
    }
    val isLightBg = bgRenk == Color(0xFFFFEB3B) || bgRenk == Color(0xFFFF9800) || bgRenk == Color(0xFFF5DEB3) || bgRenk == Color(0xFFFF5722)
    val yaziRengi = if (isLightBg) Color.Black else Color.White
    val fiyatRengi = if (bgRenk == Color(0xFF242424)) MaterialTheme.colorScheme.primary else if (isLightBg) Color(0xFF333333) else Color.White

    Card(modifier = Modifier.fillMaxWidth().height(120.dp).pointerInput(Unit) { detectTapGestures(onTap = { onClick() }, onLongPress = { onLongClick() }) }, shape = RoundedCornerShape(16.dp), elevation = CardDefaults.cardElevation(defaultElevation = 8.dp), colors = CardDefaults.cardColors(containerColor = bgRenk)) {
        Column(modifier = Modifier.padding(12.dp).fillMaxSize(), verticalArrangement = Arrangement.Center, horizontalAlignment = Alignment.CenterHorizontally) {
            Text(text = urun.ad, fontSize = 20.sp, fontWeight = FontWeight.Bold, color = yaziRengi, textAlign = TextAlign.Center, maxLines = 2, lineHeight = 24.sp, overflow = TextOverflow.Ellipsis)
            Spacer(modifier = Modifier.height(8.dp))
            Text(text = "${urun.secenekler.first().fiyat} ₺", fontSize = 15.sp, color = fiyatRengi, fontWeight = FontWeight.ExtraBold)
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class, ExperimentalFoundationApi::class)
@Composable
fun SiparisBottomSheet(urun: Urun, guncelMasaAdi: String?, icecekMenusu: List<Urun>, ucretliEkstralar: Map<String, Int>, kapat: () -> Unit, onSiparisEkle: (String, List<SiparisKalemi>) -> Unit) {
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)
    val haptic = LocalHapticFeedback.current
    var seciliGramaj by remember { mutableStateOf(urun.secenekler.find { it.gramaj == "100gr" } ?: urun.secenekler.first()) }
    var siparisNotu by remember { mutableStateOf("") }
    var musteriAdi by remember { mutableStateOf("") }
    var adet by remember { mutableIntStateOf(1) }
    val isIcecek = icecekMenusu.any { it.ad == urun.ad }

    val seciliNotlar = remember { mutableStateMapOf<String, Boolean>() }
    val seciliUcretsizEkstralar = remember { mutableStateMapOf<String, Boolean>() }
    val seciliUcretliEkstralar = remember { mutableStateMapOf<String, Boolean>() }
    val seciliOdemeler = remember { mutableStateMapOf<String, Boolean>() }
    val seciliIcecekler = remember { mutableStateMapOf<String, Boolean>() }
    val icecekAdetleri = remember { mutableStateMapOf<String, Int>() }
    LaunchedEffect(urun) { icecekMenusu.forEach { icecekAdetleri[it.ad] = 1 } }

    val ekstralarFiyati = seciliUcretliEkstralar.filter { it.value }.keys.sumOf { ucretliEkstralar[it] ?: 0 }
    val anlikBirimFiyat = seciliGramaj.fiyat + ekstralarFiyati
    val toplamTutar = (anlikBirimFiyat * adet) + icecekMenusu.filter { seciliIcecekler[it.ad] == true }.sumOf { (it.secenekler.first().fiyat * (icecekAdetleri[it.ad] ?: 1)) }

    ModalBottomSheet(onDismissRequest = kapat, sheetState = sheetState, containerColor = Color(0xFF1E1E1E)) {
        Column(modifier = Modifier.fillMaxWidth().verticalScroll(rememberScrollState()).padding(horizontal = 20.dp, vertical = 8.dp)) {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Text(urun.ad, fontWeight = FontWeight.Black, color = Color.White, fontSize = 28.sp, modifier = Modifier.weight(1f))
                Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.background(Color(0xFF333333), RoundedCornerShape(12.dp)).padding(8.dp)) {
                    IconButton(onClick = { if (adet > 1) { adet--; haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove) } }, modifier = Modifier.size(40.dp)) { Text("-", color = Color.White, fontSize = 28.sp, fontWeight = FontWeight.Bold) }
                    Text("$adet", color = Color(0xFFFF9800), fontSize = 24.sp, fontWeight = FontWeight.ExtraBold, modifier = Modifier.padding(horizontal = 16.dp))
                    IconButton(onClick = { adet++; haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove) }, modifier = Modifier.size(40.dp)) { Text("+", color = Color.White, fontSize = 28.sp, fontWeight = FontWeight.Bold) }
                }
            }
            Spacer(modifier = Modifier.height(12.dp))
            Text("Seçim / Gramaj", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary, fontSize = 15.sp)
            FlowRow(horizontalArrangement = Arrangement.spacedBy(6.dp), modifier = Modifier.padding(top = 4.dp)) {
                urun.secenekler.forEach { sec -> FilterChip(selected = (seciliGramaj == sec), onClick = { seciliGramaj = sec }, label = { Text(if(sec.gramaj == "Standart") "${sec.fiyat} ₺" else "${sec.gramaj} (${sec.fiyat}₺)", fontSize = 13.sp, fontWeight = FontWeight.Bold) }, colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Color(0xFF4CAF50), selectedLabelColor = Color.White)) }
            }
            Spacer(modifier = Modifier.height(8.dp))

            if (!isIcecek) {
                Text("Icerik", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary, fontSize = 15.sp)
                FlowRow(horizontalArrangement = Arrangement.spacedBy(6.dp), modifier = Modifier.padding(top = 4.dp)) {
                    val zityon = mapOf("Sogansiz" to "Soganli", "Soganli" to "Sogansiz", "Domatessiz" to "Domatesli", "Domatesli" to "Domatessiz", "Patatessiz" to "Patatesli", "Patatesli" to "Patatessiz", "Ketcapsiz" to "Ketcapli", "Ketcapli" to "Ketcapsiz", "Mayonezsiz" to "Mayonezli", "Mayonezli" to "Mayonezsiz", "Tursusuz" to "Tursulu", "Tursulu" to "Tursusuz")
                    val cikar = listOf("Sogansiz", "Domatessiz", "Patatessiz", "Ketcapsiz", "Mayonezsiz", "Tursusuz")
                    val ekle = listOf("Soganli", "Domatesli", "Patatesli", "Ketcapli", "Mayonezli", "Tursulu")
                    cikar.forEach { malz -> FilterChip(selected = seciliNotlar[malz] == true, onClick = { val s = !(seciliNotlar[malz] ?: false); seciliNotlar[malz] = s; if(s && zityon.containsKey(malz)) seciliNotlar[zityon[malz]!!] = false }, label = { Text(malz, fontSize = 13.sp) }, colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Color(0xFFE53935), selectedLabelColor = Color.White)) }
                    ekle.forEach { malz -> FilterChip(selected = seciliNotlar[malz] == true, onClick = { val s = !(seciliNotlar[malz] ?: false); seciliNotlar[malz] = s; if(s && zityon.containsKey(malz)) seciliNotlar[zityon[malz]!!] = false }, label = { Text(malz, fontSize = 13.sp) }, colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Color(0xFF4CAF50), selectedLabelColor = Color.White)) }
                    listOf("Cheddar", "Kasarli").forEach { malz -> if(ucretliEkstralar.containsKey(malz)) { FilterChip(selected = seciliUcretliEkstralar[malz] == true, onClick = { seciliUcretliEkstralar[malz] = !(seciliUcretliEkstralar[malz] ?: false) }, label = { Text(malz, fontSize = 13.sp) }, colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Color(0xFFFFD54F), selectedLabelColor = Color.Black)) } }
                }
                Spacer(modifier = Modifier.height(8.dp))

                val digerUcretliler = ucretliEkstralar.filterKeys { !it.contains("Cheddar") && !it.contains("Kasar") && !it.contains("Kaşar") }
                if (digerUcretliler.isNotEmpty()) {
                    Text("Ucretli Ekstralar", fontWeight = FontWeight.Bold, color = Color(0xFFFFD54F), fontSize = 15.sp)
                    FlowRow(horizontalArrangement = Arrangement.spacedBy(12.dp), modifier = Modifier.padding(top = 8.dp)) {
                        digerUcretliler.forEach { (isim, fiyat) -> FilterChip(selected = seciliUcretliEkstralar[isim] == true, onClick = { seciliUcretliEkstralar[isim] = !(seciliUcretliEkstralar[isim] ?: false) }, label = { Text("$isim (+$fiyat₺)", fontSize = 15.sp, modifier = Modifier.padding(6.dp)) }, colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Color(0xFFFFD54F), selectedLabelColor = Color.Black)) }
                    }
                    Spacer(modifier = Modifier.height(8.dp))
                }

                Row(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text("Ozel Not Gir:", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary, fontSize = 15.sp)
                        FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) { ucretsiz_ekstra_listesi.forEach { eks -> FilterChip(selected = seciliUcretsizEkstralar[eks] == true, onClick = { seciliUcretsizEkstralar[eks] = !(seciliUcretsizEkstralar[eks] ?: false) }, label = { Text(eks, fontSize = 13.sp) }) } }
                    }
                    Column(modifier = Modifier.weight(1f)) {
                        Text("Odeme", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary, fontSize = 15.sp)
                        FlowRow(horizontalArrangement = Arrangement.spacedBy(6.dp)) { odeme_listesi.forEach { odm -> FilterChip(selected = seciliOdemeler[odm] == true, onClick = { 
                            val newVal = !(seciliOdemeler[odm] ?: false)
                            seciliOdemeler[odm] = newVal
                            if (newVal) {
                                if (odm == "POS") seciliOdemeler["NAKİT"] = false
                                if (odm == "NAKİT") seciliOdemeler["POS"] = false
                                if (odm == "Paket") seciliOdemeler["Dükkan içi"] = false
                                if (odm == "Dükkan içi") seciliOdemeler["Paket"] = false
                            }
                        }, label = { Text(odm, fontSize = 13.sp) }) } }
                    }
                }
                Spacer(modifier = Modifier.height(8.dp))

                Text("Hızlı İçecek Ekle", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary, fontSize = 15.sp)
                val currentViewConfig = androidx.compose.ui.platform.LocalViewConfiguration.current
                val fastLongPressConfig = androidx.compose.runtime.remember(currentViewConfig) {
                    object : androidx.compose.ui.platform.ViewConfiguration by currentViewConfig {
                        override val longPressTimeoutMillis: Long = 200L
                    }
                }
                androidx.compose.runtime.CompositionLocalProvider(androidx.compose.ui.platform.LocalViewConfiguration provides fastLongPressConfig) {
                FlowRow(modifier = Modifier.fillMaxWidth().padding(top = 8.dp), horizontalArrangement = Arrangement.SpaceBetween, verticalArrangement = Arrangement.spacedBy(12.dp), maxItemsInEachRow = 5) {
                    icecekMenusu.forEach { ic ->
                        val miktar = if (seciliIcecekler[ic.ad] == true) (icecekAdetleri[ic.ad] ?: 1) else 0
                        Box(contentAlignment = Alignment.TopEnd) {
                            Box(
                                modifier = Modifier
                                    .height(50.dp).width(68.dp)
                                    .background(
                                        color = when {
                                            ic.ad.lowercase().contains("kutu kola") || ic.ad.lowercase().contains("şişe kola") -> Color(0xFFF40009)
                                            ic.ad.lowercase().contains("sprite") -> Color(0xFF008B47)
                                            ic.ad.lowercase().contains("fanta") -> Color(0xFFF58216)
                                            ic.ad.lowercase().contains("ayran") -> Color(0xFFFDFD96)
                                            ic.ad.lowercase().contains("su") && !ic.ad.lowercase().contains("usul") -> Color(0xFF00BFFF)
                                            ic.ad.lowercase().contains("soda") -> Color(0xFF006400)
                                            ic.ad.lowercase().contains("şalgam") -> Color(0xFF800080)
                                            ic.ad.lowercase().contains("zero") -> Color(0xFF111111)
                                            else -> Color(0xFF242424)
                                        }.let { if (miktar > 0) it else it.copy(alpha = 0.4f) },
                                        shape = RoundedCornerShape(12.dp)
                                    )
                                    .combinedClickable(
                                        onClick = { 
                                            haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                                            if (miktar == 0) {
                                                seciliIcecekler[ic.ad] = true
                                                icecekAdetleri[ic.ad] = 1
                                            } else {
                                                icecekAdetleri[ic.ad] = miktar + 1
                                            }
                                        },
                                        onLongClick = { 
                                            if (miktar > 0) {
                                                haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                                                if (miktar == 1) {
                                                    seciliIcecekler[ic.ad] = false
                                                    icecekAdetleri[ic.ad] = 1
                                                } else {
                                                    icecekAdetleri[ic.ad] = miktar - 1
                                                }
                                            }
                                        }
                                    ),
                                contentAlignment = Alignment.Center
                            ) {
                                val yRengi = if (ic.ad.lowercase().contains("ayran")) Color.Black else Color.White
                                Text(ic.ad, color = yRengi, fontSize = 11.sp, fontWeight = FontWeight.Bold, textAlign = TextAlign.Center, modifier = Modifier.padding(2.dp), lineHeight = 12.sp)
                            }
                            
                            if (miktar > 0) {
                                Box(
                                    modifier = Modifier
                                        .offset(x = 6.dp, y = (-6).dp)
                                        .size(28.dp)
                                        .background(Color(0xFFD32F2F), CircleShape),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Text(text = "$miktar", color = Color.White, fontSize = 14.sp, fontWeight = FontWeight.ExtraBold)
                                }
                            }
                        }

                            }

                        }

                        }

                        }
            Spacer(modifier = Modifier.height(8.dp))
            OutlinedTextField(value = siparisNotu, onValueChange = { siparisNotu = it }, label = { Text("Özel Sipariş Notu (Örn: Çok pişsin)", fontSize = 15.sp) }, modifier = Modifier.fillMaxWidth(), textStyle = androidx.compose.ui.text.TextStyle(fontSize = 20.sp))
            if (guncelMasaAdi == null) {
                Spacer(modifier = Modifier.height(16.dp))
                OutlinedTextField(value = musteriAdi, onValueChange = { musteriAdi = it }, label = { Text("Masa No / İsim", fontSize = 15.sp) }, singleLine = true, modifier = Modifier.fillMaxWidth(), textStyle = androidx.compose.ui.text.TextStyle(fontSize = 20.sp))
            }
            Spacer(modifier = Modifier.height(16.dp))
            
            Button(
                onClick = {
                    val kalemler = mutableListOf<SiparisKalemi>()
                    val tumNotlar = mutableListOf<String>()
                    tumNotlar.addAll(seciliNotlar.filter { it.value }.map { it.key })
                    tumNotlar.addAll(seciliUcretsizEkstralar.filter { it.value }.map { it.key })
                    tumNotlar.addAll(seciliUcretliEkstralar.filter { it.value }.map { "${it.key} eklendi" }) 
                    tumNotlar.addAll(seciliOdemeler.filter { it.value }.map { it.key })
                    if (siparisNotu.isNotBlank()) tumNotlar.add(siparisNotu.trim())
                    val notMetni = if (tumNotlar.isNotEmpty()) "Not: ${tumNotlar.joinToString(", ")}" else ""

                    repeat(adet) { kalemler.add(SiparisKalemi(urun.ad, seciliGramaj.gramaj, anlikBirimFiyat, notMetni)) }
                    icecekMenusu.forEachIndexed { _, ic -> if (seciliIcecekler[ic.ad] == true) { val icAdet = icecekAdetleri[ic.ad] ?: 1; repeat(icAdet) { kalemler.add(SiparisKalemi(ic.ad, "Standart", ic.secenekler.first().fiyat, "")) } } }
                    onSiparisEkle(musteriAdi, kalemler)
                }, modifier = Modifier.fillMaxWidth().height(64.dp), colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFFF9800)), shape = RoundedCornerShape(16.dp)
            ) { Text("Sepete Ekle - TOPLAM: $toplamTutar ₺", color = Color.Black, fontWeight = FontWeight.Black, fontSize = 20.sp) }
            Spacer(modifier = Modifier.height(40.dp))
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AdisyonKarti(adisyon: Adisyon, tamamlandiClick: () -> Unit, kalemSilClick: (SiparisKalemi) -> Unit, ilaveClick: () -> Unit, notDuzenleClick: (SiparisKalemi) -> Unit, yazdirClick: () -> Unit) {
    val genisletilmisGruplar = remember { mutableStateMapOf<String, Boolean>() }
    val grupluKalemler = adisyon.kalemler.groupBy { "${it.urunAd}_${it.detay}_${it.notlar}" }
    val kartRengi = if (adisyon.durum == "Bekliyor") Color(0xFF242424) else Color(0xFF1b2b20)

    Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(16.dp), elevation = CardDefaults.cardElevation(defaultElevation = 8.dp), colors = CardDefaults.cardColors(containerColor = kartRengi)) {
        Column(modifier = Modifier.padding(20.dp)) {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Row(modifier = Modifier.weight(1f), verticalAlignment = Alignment.CenterVertically) {
                    if (!adisyon.renk.isNullOrBlank()) {
                        val pColor = try { android.graphics.Color.parseColor(adisyon.renk) } catch(e: Exception) { android.graphics.Color.TRANSPARENT }
                        if (pColor != android.graphics.Color.TRANSPARENT) {
                            Box(modifier = Modifier.size(16.dp).background(Color(pColor), CircleShape))
                            Spacer(modifier = Modifier.width(8.dp))
                        }
                    }
                    Text(text = "${adisyon.musteriAdi} ${if (adisyon.saat.isNotBlank()) "(${adisyon.saat})" else ""}", fontWeight = FontWeight.Black, fontSize = 24.sp, color = Color.White, maxLines = 1, overflow = TextOverflow.Ellipsis)
                }
                Text(text = "${adisyon.toplamTutar} ₺", fontWeight = FontWeight.Black, fontSize = 24.sp, color = Color(0xFF4CAF50), modifier = Modifier.padding(start = 8.dp))
            }
            Divider(modifier = Modifier.padding(vertical = 12.dp), color = Color(0xFF424242))

            grupluKalemler.forEach { (grupAnahtari, kalemListesi) ->
                val ilkKalem = kalemListesi.first(); val adet = kalemListesi.size; val isExpanded = genisletilmisGruplar[grupAnahtari] == true

                Row(modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp).clickable { genisletilmisGruplar[grupAnahtari] = !isExpanded }, horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                    Column(modifier = Modifier.weight(1f)) {
                        val detayText = if (ilkKalem.detay == "Standart") "" else " (${ilkKalem.detay})"
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(text = "• ${adet}x ${ilkKalem.urunAd}$detayText", fontSize = 20.sp, fontWeight = FontWeight.Bold, color = Color.White)
                            if (adet > 1) Text(text = if (isExpanded) "  ▲" else "  ▼", fontSize = 13.sp, color = Color.Gray)
                        }
                        if (ilkKalem.notlar.isNotEmpty()) Text(text = ilkKalem.notlar, fontSize = 13.sp, color = Color.LightGray, modifier = Modifier.padding(top = 4.dp))
                    }
                    Text(text = "${ilkKalem.fiyat * adet} ₺", fontSize = 20.sp, fontWeight = FontWeight.Bold, color = Color(0xFF81C784))
                }

                if (isExpanded || adet == 1) {
                    Column(modifier = Modifier.fillMaxWidth().background(Color(0xFF1E1E1E), RoundedCornerShape(12.dp)).clip(RoundedCornerShape(12.dp))) {
                        kalemListesi.forEach { tekliKalem ->
                            key(System.identityHashCode(tekliKalem)) {
                            var isDeleted by remember { mutableStateOf(false) }
                                val dismissState = rememberSwipeToDismissBoxState(confirmValueChange = { 
                                    if (it == SwipeToDismissBoxValue.EndToStart) {
                                        if (!isDeleted) {
                                            isDeleted = true
                                            kalemSilClick(tekliKalem)
                                        }
                                        true 
                                    } else false 
                                })
                            SwipeToDismissBox(state = dismissState, enableDismissFromStartToEnd = false, backgroundContent = { val color by animateColorAsState(if (dismissState.targetValue == SwipeToDismissBoxValue.EndToStart) Color.Red else Color.Transparent); Box(Modifier.fillMaxSize().background(color).padding(horizontal = 20.dp), contentAlignment = Alignment.CenterEnd) { Text("Sil", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 15.sp) } }) {
                                Row(modifier = Modifier.fillMaxWidth().background(Color(0xFF1E1E1E)).padding(horizontal = 16.dp, vertical = 12.dp), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                                    Text(text = "↳ 1x ${tekliKalem.urunAd}", fontSize = 13.sp, color = Color.LightGray)
                                    Row(verticalAlignment = Alignment.CenterVertically) {
                                        Text(text = "${tekliKalem.fiyat} ₺", fontSize = 13.sp, color = Color.Gray, modifier = Modifier.padding(end = 12.dp))
                                        Box(modifier = Modifier.size(36.dp).background(Color(0xFF333333), RoundedCornerShape(8.dp)).clickable { notDuzenleClick(tekliKalem) }, contentAlignment = Alignment.Center) { Text("✏️", fontSize = 13.sp) }
                                        Spacer(modifier = Modifier.width(8.dp))
                                        Box(modifier = Modifier.size(36.dp).background(Color(0xFF421515), RoundedCornerShape(8.dp)).clickable { kalemSilClick(tekliKalem) }, contentAlignment = Alignment.Center) { Text("🗑️", fontSize = 13.sp) }
                                    }
                                }
                            }
                            }
                        }
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            if (adisyon.durum == "Bekliyor") {
                OutlinedButton(onClick = ilaveClick, modifier = Modifier.fillMaxWidth().height(56.dp), colors = ButtonDefaults.outlinedButtonColors(contentColor = Color(0xFFFF9800)), border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFFF9800)), shape = RoundedCornerShape(12.dp)) { Text("Siparişi Düzenle (Ekle)", fontWeight = FontWeight.Bold, fontSize = 15.sp) }
                Spacer(modifier = Modifier.height(12.dp))
            }
            Row(modifier = Modifier.fillMaxWidth()) {
                Button(onClick = yazdirClick, modifier = Modifier.weight(1f).height(64.dp), colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF424242)), shape = RoundedCornerShape(12.dp)) { Text("🖨️ Fiş Yazdır", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 15.sp) }
                Spacer(modifier = Modifier.width(12.dp))
                Button(onClick = tamamlandiClick, modifier = Modifier.weight(1f).height(64.dp), colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2E7D32)), shape = RoundedCornerShape(12.dp)) { Text("Ödendi / Kapat", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 15.sp) }
            }
        }
    }
}